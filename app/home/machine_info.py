import os
import platform
import psutil
import time
#import path
from ..models import Department, Employee, Role, Upload
from sqlalchemy import func
from .. import db
#measureing tool candidates
MTC_files = '/home/pi/prj/scripts/chalice/raspieye/app/static/img/unified_image_set/measures/.'
#user uploaded search candidates
SC_files = '/home/pi/prj/scripts/chalice/raspieye/app/static/img/unified_image_set/Search_Candidates/.'
#search base of indexed images
SB_files = '/home/pi/prj/scripts/chalice/raspieye/app/static/img/unified_image_set/Search_Holidaysnaps/.'
#document scanner candidates
DS_files = '/home/pi/prj/scripts/chalice/raspieye/app/static/img/unified_image_set/doc_scanner/.'
image_files = '/home/pi/prj/scripts/chalice/raspieye/app/static/img/unified_image_set/.'
GEN_files = '/home/pi/prj/scripts/chalice/raspieye/app/static/img/unified_image_set/uploads/.'
class machine_stats():

    def df_space(directories):
        directories = directories
        dir_info = {}

        for i in directories:

            #print('\nDirectory: ' + i)
            #print('********************')

            space_output = os.statvfs(i)
            #print(space_output)
            block_size = space_output[1]
            free_space = int((block_size * space_output[4])/(1024**3))
            total_space = int((block_size * space_output[2])/(1024**3))
            used_space = int((total_space) - (free_space))

            #print('total space: ' + str(int(total_space/(1000**3))) + '  Gb.')
            #print('used space: ' + str(int(used_space/10000)) + '  Gb used')
            #print('free space: '+ str(int(free_space/(1000**3))) + '  Gb.\n')

            dir_info[i] = [total_space, used_space, free_space]

        return dir_info, directories

    def cpu_snapshot():
        polls = {}
        count = 0
        title_list =  ['REC ', '*CPU* ','TOT_M ', '*USED_M* ', 'FREE_M']

        for i in range(1,10):

            percent = psutil.cpu_percent()
            count += 1

            if percent > 0:
                tot_m, used_m, free_m = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
                polls[count] = [percent, tot_m, used_m, free_m]
                time.sleep(3)

            else:
                time.sleep(3)


        return polls, title_list


    def db_health(db_file):

        db_file = db_file
        table_stats = {}
        data_systems = {}
        data_systems['All Images Folders (Gb)'] = int(os.path.getsize(image_files)/10024)
        data_systems['Database File (Kb)'] = os.path.getsize(db_file)/1000
        data_systems['Documents Scanner Folder (Mb)'] = int(os.path.getsize(DS_files)/1000)
        data_systems['General Uploads Folder (Mb)'] = int(os.path.getsize(GEN_files)/1000)
        data_systems['Measurement Tool Candidates Folder (Mb)'] = int(os.path.getsize(MTC_files)/1000)
        data_systems['Search Base Folder (Gb)'] = int(os.path.getsize(SB_files)/10000)
        data_systems['Search Candidates Images Folder (Mb)'] = int(os.path.getsize(SC_files)/1000)

        #data_systems['vids_filesz'] = os.path.getsize("//videopath")
        #how to query for tables in db?
        tables =[Employee, Department, Role, Upload]
        for table in tables:
            records_per_table = db.session.query(func.count(table.id)).scalar()
            table_stats[table] = records_per_table

        return table_stats, data_systems












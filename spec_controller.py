import time
import os
import imp
import sys
import datetime
import pexpect
from shutil import copyfile

dev=True
computer='new'
#computer='new'
RS3_running=True
ViewSpecPro_running=False
timeout=5
share_loc=''
RS3_loc=''
ViewSpecPro_loc=''



if computer == 'old': 
    sys.path.append('c:/users/rs3admin/hozak/python/autoasd/')
    #os.system('del C:\\SpecShare\commands\*')
    os.chdir('c:/users/rs3admin/hozak/python/autoasd')
    share_loc='C:\\SpecShare'
    RS3_loc=r"C:\Program Files\ASD\RS3\RS3.exe"
    ViewSpecPro_loc=r"C:\Program Files\ASD\ViewSpecPro\ViewSpecPro.exe"
    
elif computer =='new':
    sys.path.append('C:\\users\\hozak\\Python\\Autoasd')
    os.chdir('C:\\users\\hozak\\Python\\Autoasd')
    share_loc='C:\\SpecShare'
    RS3_loc=r"C:\Program Files (x86)\ASD\RS3\RS3.exe"
    ViewSpecPro_loc=r"C:\Program Files (x86)\ASD\ViewSpecPro\ViewSpecPro.exe"

import asdcontrols

read_command_loc=share_loc+'\\commands\\from_control'
write_command_loc=share_loc+'\\commands\\from_spec'
temp_data_loc=share_loc+'\\temp'

data_loc=share_loc
if dev:
    imp.reload(asdcontrols)
    from asdcontrols import RS3Controller
    from asdcontrols import ViewSpecProController

def main():
    print('Starting AutoASD...\n')
    cmdnum=0
    #logpath='C:/Users/RS3Admin/hozak/log.txt'
    #logpath='C:/SpecShare/log/log.txt'      
    logdir=share_loc+'\\log\\'+datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    try:
        os.mkdir(logdir)
    except(FileExistsError):
        try:
            os.mkdir(logdir+'_2')
        except:
            print('Seriously?')
    logline='test'
    open(logdir+'\\'+logline,'w+').close()
    # with open(logpath, 'w+') as log:
    #     log.write('Intiating listener on spec compy')

    print('Removing old commands and temporary data...')
    delme=os.listdir(read_command_loc)
    for file in delme:
        os.remove(read_command_loc+'\\'+file)
    print('\tCommand folder for reading clean')
    
    delme=os.listdir(write_command_loc)
    for file in delme:
        os.remove(write_command_loc+'\\'+file)
    print('\tCommand folder for writing clean')
        
    delme=os.listdir(temp_data_loc)
    for file in delme:
        os.remove(temp_data_loc+'\\'+file)
    print('\tTemporary data directory clean')
        
    print('Done.\n')
        
    # with open(write_command_loc+'\\started'+str(cmdnum),'w+') as f:
    #         pass
    # cmdnum+=1

    print('Initializing ASD connections...')
    spec_controller=RS3Controller(share_loc, RS3_loc, logdir, running=RS3_running)
    process_controller=ViewSpecProController(share_loc, ViewSpecPro_loc,logdir, running=ViewSpecPro_running)
    print('Done.\n')
    print('Ready!')
    logger=Logger()
    
    delme=os.listdir(write_command_loc)
    for file in delme:
        os.remove(write_command_loc+'\\'+file)
    
    cmdfiles0=os.listdir(read_command_loc)
    

    # with open(write_command_loc+'\\ready'+str(cmdnum),'w+') as f:
    #         pass
    #cmdnum+=1

    #wait_for_saveconfig_before_doing_instrument_config=False
    #instrument_config_num=None
    
    data_files_to_ignore=[]
    no_connection=None
    #count=0
    while True:
        #check connectivity with spectrometer
        connected=spec_controller.check_connectivity()
        if not connected:
            try:
                #Let's not accumulate 500000 files
                files=os.listdir(write_command_loc)
                # for i, file in files:
                #     if i==0:
                #         pass
                #     elif 'lostconnection' in file:
                #         os.remove(file)
                #         print(file)
                if no_connection==None or no_connection==False: #If this is the first time we've realized we aren't connected. It will be None the first time through the loop and True or False afterward.
                    print('Waiting for RS³ to connect to the spectrometer...')
                    no_connection=True #Use this to know to print an announcement if the spectrometer reconnects next time.
                #print('write!')
                with open(write_command_loc+'\\lostconnection','w+') as f:
                    pass
                files=os.listdir(write_command_loc)

            except:
                pass
            time.sleep(1)
        if connected and no_connection==True: #If we weren't connected before, let everyone know we are now!
            no_connection=False
            print('RS³ to connected to the spectrometer. Listening!')
                
        
        #check for unexpected files in data adirectory
        file=check_for_unexpected(spec_controller.save_dir, spec_controller.hopefully_saved_files, data_files_to_ignore)
        while file !=None:
            data_files_to_ignore.append(file)
            with open(write_command_loc+'\\unexpectedfile'+str(cmdnum)+'&'+file,'w+') as f:
                    pass
            cmdnum+=1
            file=check_for_unexpected(spec_controller.save_dir, spec_controller.hopefully_saved_files, data_files_to_ignore)
               
        #check for new commands in the read_command location
        cmdfiles=os.listdir(read_command_loc)

        if cmdfiles!=cmdfiles0:
            print('***************')
            for file in cmdfiles:
                if file not in cmdfiles0:
                    cmd,params=filename_to_cmd(file)
                    print('Spec compy received command: '+cmd)
                    print(file)
                    #Got already in use error before, presumably that is temporary so let's just try again if that happens
                    try:
                        os.remove(read_command_loc+'\\'+file)
                    except PermissionError as e:
                        time.sleep(1)
                        os.remove(read_command_loc+'\\'+file)
                    # if not connected:
                    #     print('not connected')
                    #     if 'retryconnection' in cmd:
                    #         connected=spec_controller.check_connectivity()
                    #         if connected:
                    #             print('reconnected')
                    #         else:
                    #             continue
                    #     else:
                    #         time.sleep(0.25)
                    #         continue
                    if 'checkwriteable' in cmd:
                        try:
                            os.mkdir(params[0]+'\\autospec_temp')
                            os.removedirs(params[0]+'\\autospec_temp')
                            print('writeable')
                            with open(write_command_loc+'\\yeswriteable'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            #writeable=False
                            print('not writeable')
                            with open(write_command_loc+'\\notwriteable'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                    #os.remove(read_command_loc+'\\'+file)
                    elif 'spectrum' in cmd: 

                        if spec_controller.save_dir=='':
                            with open(write_command_loc+'\\noconfig'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        if spec_controller.numspectra==None:
                            with open(write_command_loc+'\\nonumspectra'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        
                        
                        
                        filename=''
                        if computer=='old':
                            filename=params[0]+'\\'+params[1]+'.'+params[2]
                        elif computer=='new':
                            filename=params[0]+'\\'+params[1]+params[2]+'.asd'
                            
                        label=params[3]
                        i=params[4]
                        e=params[5]
                        
                        #Check if the file already exists.
                        exists=False
                        if os.path.isfile(filename):
                            exists=True
                            with open(write_command_loc+'\\savespecfailedfileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                            
                        #After saving a spectrum, the spec_controller updates its list of expected files to include one more. Wait for this number to change before moving on.
                        old=len(spec_controller.hopefully_saved_files)
                             
                        spec_controller.take_spectrum(filename)

                        while True:
                            time.sleep(0.2)
                            new=len(spec_controller.hopefully_saved_files)
                            if new>old:
                                break
                                
                        #Now wait for the data file to turn up where it belongs.
                        saved=False
                        t0=time.clock()
                        t=time.clock()
                        while t-t0<int(spec_controller.numspectra)*4 and saved==False: #Depending on the number of spectra we are averaging, this might take a while.
                            saved=os.path.isfile(filename)
                            time.sleep(0.2)
                            t=time.clock()
                        print(filename+' saved and found?:'+ str(saved))
                        # spec_controller.numspectra=str(int(spec_controller.numspectra)-1)
                        # spec_controller.numspectra=str(int(spec_controller.numspectra)+1)
                        if saved:
                            logger.log_spectrum(spec_controller.numspectra, i, e, filename, label)
                            filestring=cmd_to_filename('savedfile'+str(cmdnum),[filename])
                        else:
                            spec_controller.hopefully_saved_files.pop(-1)
                            #spec_controller.numspectra=str(int(spec_controller.numspectra)-1)
                            spec_controller.nextnum=str(int(spec_controller.nextnum)-1)
                            filestring=cmd_to_filename('failedtosavefile'+str(cmdnum),[filename])
                            
                        with open(write_command_loc+'\\'+filestring,'w+') as f:
                            pass
                        cmdnum+=1
                        
                    elif 'saveconfig' in cmd:
                        save_path=params[0]

                        file=check_for_unexpected(save_path, spec_controller.hopefully_saved_files, data_files_to_ignore)
                        found_unexpected=False
                        while file !=None:
                            found_unexpected=True
                            data_files_to_ignore.append(file)
                            with open(write_command_loc+'\\unexpectedfile'+str(cmdnum)+'&'+file,'w+') as f:
                                    pass
                            cmdnum+=1
                            file=check_for_unexpected(save_path, spec_controller.hopefully_saved_files, data_files_to_ignore)
                        if found_unexpected==True:
                            time.sleep(2)
                        with open(write_command_loc+'\\donelookingforunexpected'+str(cmdnum),'w+') as f:
                                    pass
                        
                        basename=params[1]
                        startnum=params[2]
                        filename=''
                        if computer=='old':
                            filename=save_path+'\\'+basename+'.'+startnum
                        elif computer=='new':
                            filename=save_path+'\\'+basename+startnum+'.asd'
                        
                        if os.path.isfile(filename):
                            with open(write_command_loc+'\\saveconfigfailedfileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            skip_spectrum()

                            cmdfiles0=cmdfiles
                            continue
                        try:
                            spec_controller.spectrum_save(save_path, basename, startnum)
                            if spec_controller.failed_to_open:
                                spec_controller.failed_to_open=False
                                with open(write_command_loc+'\\saveconfigerror'+str(cmdnum),'w+') as f:
                                    pass
                                cmdnum+=1
                                skip_spectrum()
                            else:
                                logger.logfile=find_logfile(save_path)
                                if logger.logfile==None:
                                    logger.logfile=make_logfile(save_path)
                                print('LOGFILE FOR WRITING:')
                                print(logger.logfile)
                                with open(write_command_loc+'\\saveconfigsuccess'+str(cmdnum),'w+') as f:
                                    pass
                                    cmdnum+=1
                        except Exception as e:
                            spec_controller.failed_to_open=False
                            with open(write_command_loc+'\\saveconfigerror'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            skip_spectrum()
                            instrument_config_num=None



                            
                    elif 'wr' in cmd and 'writeable' not in cmd: 
                        if spec_controller.save_dir=='':
                            with open(write_command_loc+'\\noconfig'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        if spec_controller.numspectra==None:
                            with open(write_command_loc+'\\nonumspectra'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                            
                        if computer=='old':
                            filename=spec_controller.save_dir+'\\'+spec_controller.basename+'.'+spec_controller.nextnum
                        elif computer=='new':
                            filename=spec_controller.save_dir+'\\'+spec_controller.basename+spec_controller.nextnum+'.asd'
                        exists=False
                        
                        if os.path.isfile(filename):
                            
                            exists=True
                            with open(write_command_loc+'\\wrfailedfileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        spec_controller.white_reference()

                        if spec_controller.wr_success==True:
                            with open(write_command_loc+'\\wrsuccess'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        else:
                            with open(write_command_loc+'\\wrfailed'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        spec_controller.wr_success=False
                        spec_controller.wr_failure=False
                        
                    elif 'opt' in cmd: 
                        if spec_controller.save_dir=='':
                            with open(write_command_loc+'\\noconfig'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                            
                        if spec_controller.numspectra==None:
                            with open(write_command_loc+'\\nonumspectra'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        try:
                            spec_controller.optimize()
                            if spec_controller.opt_complete==True:
                                logger.log_opt()
                                with open(write_command_loc+'\\optsuccess'+str(cmdnum),'w+') as f:
                                    pass
                                cmdnum+=1
                            else:
                                with open(write_command_loc+'\\optfailure'+str(cmdnum),'w+') as f:
                                    pass
                                cmdnum+=1
                        except:
                            with open(write_command_loc+'\\optfailure'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                   
                    elif 'process' in cmd:
                        input_path=params[0] 
                        print(input_path)                           
                        output_path=params[1]
                        print(output_path)
                        tsv_name=params[2]
                        logfile_for_reading=params[3]
                        print(logfile)
                        
                        if input_path=='spec_share_loc':
                            input_path=share_loc
                        if output_path=='spec_share_loc':
                            output_path=share_loc
                        if logfile_for_reading=='proc_temp_log.txt':
                            logfile_for_reading=share_loc+'\\temp\\proc_temp_log.txt'
                        elif logfile_for_reading=='None':
                            print('here are files we are looking at')
                            for potential_log in os.listdir(input_path):
                                if '.txt' in potential_log:
                                    try:
                                        with open(input_path+'\\'+potential_log, 'r') as f:
                                            firstline=f.readline()
                                            print(firstline)
                                            if '#AutoSpec log' in firstline:
                                                logfile_for_reading=input_path+'\\'+potential_log
                                                print(logfile_for_reading)
                                                break
                                    except Exception as e:
                                        print(e)
                        
                        if os.path.isfile(output_path+'\\'+tsv_name):
                            with open(write_command_loc+'\\processerrorfileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            cmdfiles0=cmdfiles
                            continue
                        writeable=os.access(output_path,os.W_OK)
                        try:
                            print(output_path+'\\delme')
                            os.mkdir(output_path+'\\delme')
                            os.removedirs(output_path+'\\delme')
                        except:
                            writeable=False
                       
                        if not writeable:
                            with open(write_command_loc+'\\processerrorcannotwrite'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                        #If the specified output path is in the C drive, we can write straight to it. Otherwise, we're going to temporarily store the file in C:\\SpecShare\\temp
                        else:
                            if output_path[0:3]!='C:\\':
                                temp_output_path='C:\\SpecShare\\temp'
                            else:
                                temp_output_path=output_path
                            
                            datafile=temp_output_path+'\\'+tsv_name

                            try:
                                process_controller.process(input_path, temp_output_path, tsv_name)
                                
                                #Check that the expected file arrived fine after processing. This sometimes wasn't happening if you fed ViewSpecPro data without taking a white reference or optimizing.
                                saved=False
                                t0=time.clock()
                                t=time.clock()
                                while t-t0<5 and saved==False:
                                    saved=os.path.isfile(datafile)
                                    time.sleep(0.2)
                                    t=time.clock()
                                if saved:
                                    #Load headers from the logfile
                                    warnings=set_headers(datafile, logfile)
                                    print(warnings)
                                    
                                    #If we need to move the final to get it to its final destination, do it!
                                    if temp_output_path!=output_path:
                                        tempfilename=datafile
                                        final_datafile=output_path+'\\'+tsv_name
                                        os.system('move '+tempfilename+' '+final_datafile)
                                    #If the output directory is the same (or within) the data directory, there's no need to alert the user to an unexpected file being introduced since clearly it was expected.
                                    if spec_controller.save_dir!=None and spec_controller.save_dir!='':
                                        if spec_controller.save_dir in final_datafile:
                                            expected=filename.split(spec_controller.save_dir)[1].split('\\')[1]
                                            spec_controller.hopefully_saved_files.append(expected)
                                            
                                    with open(write_command_loc+'\\processsuccess'+str(cmdnum),'w+') as f:
                                        pass
                                #We don't actually know for sure that processing failed because of failing to optimize or white reference, but ViewSpecPro sometimes silently fails if you haven't been doing those things.
                                else:
                                    with open(write_command_loc+'\\processerrorwropt'+str(cmdnum),'w+') as f:
                                        pass
                                cmdnum+=1
                            except:
                                process_controller.reset()
                                with open(write_command_loc+'\\processerror'+str(cmdnum),'w+') as f:
                                    pass
                                cmdnum+=1
                    elif 'instrumentconfig' in cmd:                        
                        instrument_config_num=params[0]
                        try:
                            spec_controller.instrument_config(instrument_config_num)
                            with open(write_command_loc+'\\iconfigsuccess'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            with open(write_command_loc+'\\iconfigfailure'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                    #I am really not sure what this was all about... probably delete.
                    elif 'ignorefile' in cmd:
                        print('hooray!')
                        data_files_to_ignore.append('hooray!')
                    elif 'rmfile' in cmd:
                        try:
                            delme=params[0]+'\\'+params[1]+params[2]+'.asd'
                            os.remove(delme)
                            with open(write_command_loc+'\\rmsuccess'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            with open(write_command_loc+'\\rmfailure'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                    #Used for copying remote data over to the control compy for plotting, etc
                    elif 'transferdata' in cmd:
                        source=params[0]
                        destination=params[1]

                        if params[0]=='spec_share_loc':
                            source=share_loc+'\\'+params[2]
                        if params[1]=='spec_share_loc':
                            destination=share_loc+'\\'+params[2]

                        try:
                            copyfile(source,destination)
                            with open(write_command_loc+'\\datacopied'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except Exception as e:
                            print(str(e))
                            with open(write_command_loc+'\\datafailure'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                    # elif 'senddata' in cmd:
                    #     print('source: '+params[0])
                    #     print('destination: '+params[1]
                    #     try:
                    #         copyfile(params[0],data_loc+'\\'+params[1])
                    #         with open(write_command_loc+'\\datacopied'+str(cmdnum),'w+') as f:
                    #             pass
                    #         cmdnum+=1
                    #     except Exception as e:
                    #         print(str(e))
                    #         with open(write_command_loc+'\\datafailure'+str(cmdnum),'w+') as f:
                    #             pass
                    #         cmdnum+=1
                            
                    #List directories within a folder for the remote file explorer on the control compy
                    elif 'listdir' in cmd:
                        try:
                            dir=params[0]
                            if dir[-1]!='\\':dir+='\\'
                            cmdfilename=cmd_to_filename(cmd,[params[0]])
                            files=os.listdir(dir)
                            with open(write_command_loc+'\\'+cmdfilename,'w+') as f:
                                for file in files:
                                    print(os.path.isdir(dir+file))
                                    if os.path.isdir(dir+file) and file[0]!='.':
                                        f.write(file+'\n')
                                pass
                            cmdnum+=1
                        except(PermissionError):
                            print('permission')
                            with open(write_command_loc+'\\'+'listdirfailedpermission'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        except:
                            with open(write_command_loc+'\\'+'listdirfailed'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        
                    #List directories and files in a folder for the remote file explorer on the control compy
                    elif 'listcontents' in cmd:

                        try:
                            dir=params[0]
                            if dir[-1]!='\\':dir+='\\'
                            cmdfilename=cmd_to_filename(cmd,[params[0]])
                            files=os.listdir(dir)
                            sorted_files=[]
                            for i, file in enumerate(files):
                                if os.path.isdir(dir+file) and file[0]!='.':
                                    sorted_files.append(file)
                                elif file[0]!='.':
                                    #This is a way for the control compy to differentiate files from directories
                                    sorted_files.append('~:'+file)
                            sorted_files.sort()
                            with open(write_command_loc+'\\'+cmdfilename,'w+') as f:
                                for file in sorted_files:
                                    f.write(file+'\n')
                            cmdnum+=1
                        
                        except(PermissionError):
                            print('permission')
                            with open(write_command_loc+'\\'+'listdirfailedpermission'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                        except:
                            with open(write_command_loc+'\\'+'listdirfailed'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                    
                    #make a directory
                    elif 'mkdir' in cmd:
                        try:
                            os.makedirs(params[0])
                            if spec_controller.save_dir!=None and spec_controller.save_dir!='':
                                print(params[0])
                                if '\\'.join(params[0].split('\\')[:-1])==spec_controller.save_dir:
                                    expected=params[0].split(spec_controller.save_dir)[1].split('\\')[1]
                                    spec_controller.hopefully_saved_files.append(expected)
                            
                            with open(write_command_loc+'\\'+'mkdirsuccess'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                        except(FileExistsError):
                            print(params[0])
                            with open(write_command_loc+'\\'+'mkdirfailedfileexists'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                        except(PermissionError):
                            with open(write_command_loc+'\\'+'mkdirfailedpermission'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                        except:
                            with open(write_command_loc+'\\'+'mkdirfailed'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                    
                    #Not implemented yet!
                    elif 'rmdir' in cmd:
                        try:
                            shutil.rmtree(params[0])
                            if spec_controller.save_dir!=None and spec_controller.save_dir!='':
                                print(params[0])
                                if params[0] in spec_controller.save_dir:
                                    spec_controller.save_dir=None
                            
                            with open(write_command_loc+'\\'+'rmdirsuccess'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                        except(PermissionError):
                            with open(write_command_loc+'\\'+'rmdirfailedpermission'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                            
                        except:
                            with open(write_command_loc+'\\'+'rmdirfailed'+str(cmdnum),'w+') as f:
                                pass
                            cmdnum+=1
                        
        time.sleep(0.25)
        cmdfiles0=cmdfiles
        
def filename_to_cmd(filename):
    cmd=filename.split('&')[0]
    params=filename.split('&')[1:]
    i=0
    for param in params:
        params[i]=param.replace('+','\\').replace('=',':')
        i=i+1
    return cmd,params
    
def cmd_to_filename(cmd, params):
    filename=cmd
    i=0
    for param in params:
        filename=filename+'&'+param.replace('\\','+').replace(':','=')
        i=i+1
    return filename

def skip_spectrum():
    time.sleep(2)
    print('remove spec commands')
    files=os.listdir(read_command_loc)
    #print(files)
    for file in files:
        if 'spectrum' in file:
            os.remove(read_command_loc+'\\'+file)
    #print(os.listdir(read_command_loc))
    time.sleep(1)

def check_for_unexpected(save_dir, hopefully_saved_files, data_files_to_ignore):
    data_files=[]
    try:
        data_files=os.listdir(save_dir)
    except:
        pass
    expected_files=[]
    for file in hopefully_saved_files:
        expected_files.append(file.split('\\')[-1])
    for file in data_files:
        #print('This file is here:'+file)
        if file not in data_files_to_ignore:
            if file not in expected_files:
                #print('And it is not expected.')
                return file
    return None

def find_logfile(directory):
    logfile=None
    for potential_log in os.listdir(directory):
        print(potential_log)
        if '.txt' in potential_log:
            try:
                with open(directory+'\\'+potential_log, 'r') as f:
                    firstline=f.readline()
                    print(firstline)
                    if '#AutoSpec log' in firstline:
                        logfile=directory+'\\'+potential_log
                        break
            except Exception as e:
                print(e)
    if logfile!=None:
        with open(logfile,'a') as f:
            datestring=''
            datestringlist=str(datetime.datetime.now()).split('.')[:-1]
            for d in datestringlist:
                datestring=datestring+d
            f.write('#AutoSpec log re-opened on '+datestring+'.\n\n')
    print('logfile found?')
    print(logfile)
    return logfile
    

            
def make_logfile(directory):
    files=os.listdir(directory)
    i=1
    logfile='log.txt'
    while logfile in files:
        logfile='log'+str(i)+'.txt'
        i+=1
    with open(directory+'\\'+logfile,'w+') as f:
        datestring=''
        datestringlist=str(datetime.datetime.now()).split('.')[:-1]
        for d in datestringlist:
            datestring=datestring+d
        f.write('#AutoSpec log initialized on '+datestring+'.\n\n')
        
    return directory+'\\'+logfile
    
def set_headers(datafile,logfile):
    
    labels={}
    nextfile=None
    nextnote=None
    
    if os.path.exists(logfile):
        with open(logfile) as log:
            line=log.readline()
            while line!='':
                while 'i: ' not in line and line!='':
                    line=log.readline()
                if 'i:' in line:
                    try:
                        nextnote=' (i='+line.split('i: ')[-1].strip('\n')
                    except:
                        nextnote=' (i=?'
                while 'e: ' not in line and line!='':
                    line=log.readline()
                if 'e:' in line:
                    try:
                        nextnote=nextnote+' e='+line.split('e: ')[-1].strip('\n')+')'
                    except:
                        nextnote=nextnote+' e=?)'
                while 'filename' not in line and line!='':
                    line=log.readline()
                if 'filename' in line:
                    if '\\' in line:
                        line=line.split('\\')
                    else:
                        line=line.split('/')
                    nextfile=line[-1].strip('\n')
                    nextfile=nextfile.split('.')
                    nextfile=nextfile[0]+nextfile[1]
                        
                while 'Label' not in line and line!='':
                    line=log.readline()
                if 'Label' in line:
                    nextnote=line.split('Label: ')[-1].strip('\n')+nextnote
                    
                if nextfile != None and nextnote != None:
                    nextnote=nextnote.strip('\n')
                    labels[nextfile]=nextnote
        
                    nextfile=None
                    nextnote=None
                line=log.readline()
            if len(labels)==0:
                return 'nolabels'

            else:
                data_lines=[]
                with open(datafile,'r') as data:
                    line=data.readline().strip('\n')
                    print(line)
                    data_lines.append(line)
                    while line!='':
                        line=data.readline().strip('\n')
                        data_lines.append(line)
                
                datafiles=data_lines[0].split('\t')[1:] #The first header is 'Wavelengths', the rest are file names
                    
                spectrum_labels=[]
                unknown_num=0 #This is the number of files in the datafile headers that aren't listed in the log file.
                for i, filename in enumerate(datafiles):
                    label_found=False
                    filename=filename.replace('.','')
                    spectrum_label=filename
                    if filename in labels:
                        label_found=True
                        if labels[filename]!='':
                            spectrum_label=labels[filename]
                            
                    #Sometimes the label in the file will have sco attached. Take off the sco and see if that is in the labels in the file.
                    filename_minus_sco=filename[0:-3]
                    if filename_minus_sco in labels:
                        label_found=True
                        if labels[filename_minus_sco]!='':
                            spectrum_label=labels[filename_minus_sco]
                            
                    if label_found==False:
                        unknown_num+=1
                    spectrum_labels.append(spectrum_label)
                

                    
                
                header_line=data_lines[0].split('\t')[0] #This will just be 'Wavelengths'
                for i, label in enumerate(spectrum_labels):
                    header_line=header_line+'\t'+label
                
                data_lines[0]=header_line
                
                with open(datafile,'w') as data:
                    for line in data_lines:
                        data.write(line+'\n')
            
            if unknown_num==0:
                return ''#No warnings
            elif unknown_num==1:
                return '1unknown' #This will succeed but the control computer will print a warning that not all samples were labeled. Knowing if it was one or more than one just helps with grammar.

                
            elif unknown_num>1:
                return 'unknowns'

    else:
        return 'nolog'

class Logger():
    def __init__(self):
        self.logfile=''
        
    def log_spectrum(self, numspectra, i, e, filename, label):
        if label=='GARBAGE': #These are about to be deleted. No need to log them.
            return
            
        if 'White reference' in label:
            info_string='White reference saved.'
        else:
            info_string='Spectrum saved.'
    
        info_string+='\n\tSpectra averaged: ' +numspectra+'\n\ti: '+i+'\n\te: '+e+'\n\tfilename: '+filename+'\n\tLabel: '+label+'\n'
    
        self.log(info_string)
        
    def log_opt(self):
        self.log('Instrument optimized.')
        
    def log(self, info_string):
        print('**************')
        print(self.logfile)
        print('*')
        datestring=''
        datestringlist=str(datetime.datetime.now()).split('.')[:-1]
        for d in datestringlist:
            datestring=datestring+d
            
        while info_string[0]=='\n':
            info_string=info_string[1:]
    
        space=str(80)
        if '\n' in info_string:
            lines=info_string.split('\n')
    
            lines[0]=('{1:'+space+'}{0}').format(datestring,lines[0])
            info_string='\n'.join(lines)
        else:
            info_string=('{1:'+space+'}{0}').format(datestring,info_string)
            
        if info_string[-2:-1]!='\n':
            info_string+='\n'
    
        with open(self.logfile,'a') as log:
            log.write(info_string)
            log.write('\n')

if __name__=='__main__':
    main()
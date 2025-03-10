from cmd_function import *

def call(cmd):
    if cmd == "ls":
        list_visible_contents()
    
    elif cmd == "ls -a":
        list_all_contents()

    elif cmd == "tree":
        tree()

    elif cmd == "tree -a":
        tree(show_hidden=True)

    elif cmd == "pwd":
        pwd()

    elif cmd == "mkdir -m " + cmd[9:]:
        strpar = cmd[9:].split(", ")
        for i in strpar:
            mkdir(i)

    elif cmd == "mkdir " + cmd[6:]:
        mkdir(cmd[6:])

    elif cmd == "cd " + cmd[3:]:
        cd(cmd[3:])

    elif cmd == "rmdir -m " + cmd[9:]:
        strpar = cmd[9:].split(", ")
        for i in strpar:
            rmdir(i, force=True)

    elif cmd == "rmdir -f " + cmd[9:]:
        rmdir(cmd[9:], force=True)
    
    elif cmd == "rmdir " + cmd[6:]:
        rmdir(cmd[6:])

    elif cmd == "rm -m " + cmd[6:]:
        strpar = cmd[6:].split(", ")
        for i in strpar:
            rm(i, force=True)

    elif cmd == "rm -f " + cmd[6:]:
        rm(cmd[6:], force=True)

    elif cmd == "rm "+cmd[3:]:
        rm(cmd[3:])

    elif cmd == "cp " + cmd[3:]:
        strpar = cmd[3:].split(", ")
        cp(strpar[0], strpar[1])

    elif cmd == "mv " + cmd[3:]:
        strpar = cmd[3:].split(", ")
        mv(strpar[0], strpar[1])

    elif cmd == "touch -m " + cmd[9:]:
        strpar = cmd[9:].split(", ")
        for i in strpar:
            touch(i)

    elif cmd == "touch " + cmd[6:]:
        touch(cmd[6:])

    elif cmd == "unzip " + cmd[6:]:
        unzip_file(cmd[6:])

    elif cmd == "zip " + cmd[5:]:
        strpar = cmd[5:].split(", ")
        zip_files(output_filename=strpar[1], sources=strpar[2:])
    
    elif cmd == "cat " + cmd[4:]:
        cat(cmd[4:])

    elif cmd == "head " + cmd[5:]:
        head(cmd[5:])
    
    elif cmd == "tail " + cmd[5:]:
        tail(cmd[5:])

    elif cmd == "df":
        df()

    elif cmd == 'du -h ' + cmd[6:]:
        du(cmd[6:])

    elif cmd == "du":
        du()

    elif cmd == "ps":
        ps()

    elif cmd == "kill -f " + cmd[8:]:
        kill(cmd[8:], True)

    elif cmd == "kill " + cmd[5:]:
        kill(cmd[5:])

    elif cmd == "ping " + cmd[5:]:
        ping(cmd[5:])

    elif cmd == "clear":
        clear()

    elif cmd == "shutdown "+ cmd[9:]:
        shutdown(cmd[9:])

    elif cmd == "shutdown":
        shutdown()

    elif cmd == "restart "+ cmd[8:]:
        restart(cmd[8:])

    elif cmd == "restart":
        restart()

    elif cmd in " ":
        pass

    elif cmd == "git " + cmd[4:]:
        run_git_command(cmd[4:])

    elif cmd == "python " + cmd[7:]:
        python(cmd[7:])

    elif cmd == "pip " + cmd[4:]:
        pip(cmd[4:])

    else:
        print(f"Command {cmd} Not Found!\n")

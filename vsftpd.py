import subprocess

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    while True:
        output = process.stdout.readline()
        error = process.stderr.readline()
        if output == b'' and error == b'' and process.poll() is not None:
            break
        if output:
            print(output.decode("utf-8").strip())
        if error:
            print(error.decode("utf-8").strip())

# Install necessary packages
print("Please wait!!!")
install_command = "sudo yum install vsftpd zip ftp -y"
run_command(install_command)

# Start vsftpd service and enable it
start_command = "sudo systemctl start vsftpd && sudo systemctl enable vsftpd --now && sudo systemctl status vsftpd"
run_command(start_command)

# Create FTP user and set password
username = input("Enter the FTP username: ")
password = input("Enter the FTP password: ")

# Create user without password
create_user_command = f"sudo useradd {username}"
run_command(create_user_command)

# Set the password for the user
set_password_command = f"echo {password} | sudo passwd --stdin {username}"
run_command(set_password_command)

# Create FTP directory and set permissions
create_directory_command = "sudo mkdir -p /ftp"
set_permissions_command = "sudo chmod -Rf 750 /ftp/*"
change_owner_command = "sudo chown -R {0}: /ftp".format(username)
run_command(create_directory_command)
run_command(set_permissions_command)
run_command(change_owner_command)

# Add user to vsftpd user_list
add_user_to_list_command = f"sudo bash -c 'echo {username} >> /etc/vsftpd/user_list'"
run_command(add_user_to_list_command)

# Backup and update vsftpd.conf
backup_command = "sudo cp /etc/vsftpd/vsftpd.conf /etc/vsftpd/vsftpd.conf.org"
update_vsftpd_command = "sudo bash -c '> /etc/vsftpd/vsftpd.conf'"
run_command(backup_command)
run_command(update_vsftpd_command)

# Edit vsftpd.conf with necessary configurations
vsftpd_config_content = """
anonymous_enable=NO
local_enable=YES
write_enable=YES
local_umask=022
dirmessage_enable=YES
xferlog_enable=YES
connect_from_port_20=YES
xferlog_file=/var/log/xferlog
chroot_local_user=YES
allow_writeable_chroot=YES
#user_sub_token=$USER
local_root=/ftp/
pasv_enable=YES
pasv_addr_resolve=YES
pasv_min_port=33001
pasv_max_port=33005
"""

pasv_address = input("Enter the pasv_address: ")
listen_port = input("Enter the listen_port: ")

vsftpd_config_content += f"pasv_address={pasv_address}\n"
vsftpd_config_content += f"listen_port={listen_port}\n"
vsftpd_config_content += """
userlist_file=/etc/vsftpd/user_list
userlist_deny=NO
listen=NO
listen_ipv6=YES
pam_service_name=vsftpd
userlist_enable=YES
"""

with open("/etc/vsftpd/vsftpd.conf", "a") as vsftpd_conf_file:
    vsftpd_conf_file.write(vsftpd_config_content)

# Ask for the SFTP port
#sftp_port = input("Enter the SFTP port: ")

# Add SFTP port to firewalld
firewalld_command = f"sudo firewall-cmd --permanent --add-port={listen_port}/tcp"
run_command(firewalld_command)

# Reload firewalld to apply changes
reload_firewalld_command = "sudo firewall-cmd --reload"
run_command(reload_firewalld_command)

# Configure SELinux for the SFTP port
selinux_command = f"sudo semanage port -a -t ssh_port_t -p tcp {listen_port}"
run_command(selinux_command)

start_command = "sudo systemctl restart vsftpd"
run_command(start_command)

start_command = "sudo netstat -tlpn | grep {listen_port}"
run_command(start_command)
print("Configuration completed successfully.")


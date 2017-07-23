#!/bin/sh
#
# Main CGI interface for Tazinst, the SliTaz installer.
#
# Copyright (C) 2012-2016 SliTaz GNU/Linux - BSD License
#
# Authors : Dominique Corbex <domcox@slitaz.org>
#


# restricted path
PATH="/usr/sbin:/usr/bin:/sbin:/bin"

VERSION=3.98

# Common functions from libtazpanel
. ./lib/libtazpanel
get_config

TITLE=$(_ 'TazPanel - Installer')

# export package name for gettext.
TEXTDOMAIN='installer'
export TEXTDOMAIN

# tazinst required version
TAZINST_MINIMUM_VERSION="3.8"
TAZINST_MAXIMUM_VERSION="4.99"

# tazinst setup file
INSTFILE=/root/tazinst.conf


#------
# menu
#------

case "$1" in
	menu)
		cat <<EOT
<li tabindex="0">
	<span>$(_ 'Installation')</span>
	<menu>
		<li><a data-icon="install"
			href="installer.cgi" data-root>$(_ 'Installation')</a></li>
		<li><a data-icon="slitaz"
			href="installer.cgi?page=install" data-root>$(_ 'Install SliTaz')</a></li>
		<li><a data-icon="upgrade"
			href="installer.cgi?page=upgrade" data-root>$(_ 'Upgrade system')</a></li>
		<li><a data-icon="slitaz"
			href="installer.cgi?page=evaluate" data-root>$(_ 'Evaluate SliTaz')</a></li>
	</menu>
</li>
EOT
	exit
esac


#-----------
# home page
#-----------

select_action() {
	cat <<EOT
<!-- Welcome message -->

<h2>$(_ 'Welcome to the SliTaz Installer!')</h2>

<p>$(_ "The SliTaz Installer installs or upgrades SliTaz to a \
hard disk drive from a device like a Live-CD or LiveUSB key, from a SliTaz \
ISO file, or from the web by downloading an ISO file.")</p>

<p>$(_ "Windows&trade; users can evaluate SliTaz in the directory \
\\slitaz on their hard disk.")</p>

<p>$(_ "Which type of installation do you want to start?")</p>
EOT
}


select_install() {
	cat <<EOT
<!-- Install message -->

<section>
	<header>$(_ 'Install')</header>

	<div>
		<p>$(_ "Install SliTaz on a partition of your hard disk drive. If \
you decide to format your partition, all data will be lost. If you do not \
format, all data except for any existing /home directory will be removed \
(the home directory will be kept as is).")</p>
		<p>$(_ "Before installation, you may need to create or resize \
partitions on your hard disk drive in order to make space for SliTaz \
GNU/Linux. You can graphically manage your partitions with Gparted")</p>
	</div>

	<footer>
		<form>
			<button name="page" value="install" data-icon="slitaz"
				title="$(_ 'Proceed to a new SliTaz installation')"
				>$(_ 'Install SliTaz')</button>
		</form>
	</footer>
</section>
EOT
}


select_upgrade() {
	cat <<EOT
<!-- Upgrade message -->

<section>
	<header>$(_ 'Upgrade')</header>

	<div>
		<p>$(_ "Upgrade an already installed SliTaz system on your hard disk \
drive. Your /home /etc /var/www directories will be kept, all other \
directories will be removed. Any additional packages added to your old \
SliTaz system will be updated as long you have an active internet connection.")</p>
	</div>

	<footer>
		<form>
			<button name="page" value="upgrade" data-icon="upgrade"
				title="$(_ 'Upgrade an existing SliTaz system')"
				>$(_ 'Upgrade SliTaz')</button>
		</form>
	</footer>
</section>
EOT
}


select_evaluate() {
	cat <<EOT
<!-- Evaluate message -->

<section>
	<header>$(_ 'Evaluate: Without Partitioning / Formating')</header>

	<div>
	<p>$(_ 'SliTaz and Windows&trade; can coexist in the same partition.')</p>
	<p>$(_ "SliTaz will be in the %s directory like UMSDOS used to do \
in the previous century..." '\slitaz')</p>
	</div>

	<footer>
		<form action="boot.cgi">
			<input type="hidden" name="iso"/>
			<input type="hidden" name="action" value="install"/>
			<table>
			<tr><td>$(_ 'ISO image file full path')
				<span data-img="info" title="$(_ 'set %s for a physical CD-ROM' '/dev/cdrom')"></span>
			</td>
			<td>$(file_chooser "iso" "")</td></tr>
			<tr><td>$(_ 'Target partition')</td>
			<td><select name="instdev">
				<option value="/dev/null">$(_ 'Choose a partition')</option>
EOT
	blkid | grep -iE "(msdos|vfat|ntfs|ext[234]|xfs|btrfs)" | \
		sed -e 's|[A-Z]*ID="[^"]*"||g;s| SEC[^ ]*||;s|LABEL=||;s|:||' \
		    -e 's|TYPE="\([^"]*\)"|\1|;s|/dev/||' | \
	while read dev label type; do
		echo -n "<option value=\"/dev/$dev\">/dev/$dev $label $type "
		echo "$(blk2h < /sys/block/${dev:0:3}/$dev/size)</option>"
	done 
	cat <<EOT
			</select></td></tr>
			</table>
			<button data-icon="install">$(_ 'Install')</button>
		</form>
	</footer>
</section>
EOT
}


#--------------------
# partitioning page
#--------------------

exec_gparted() {
	/bin/su - -c \
	"exec env DISPLAY=':0.0' XAUTHORITY='/var/run/slim.auth' /usr/sbin/gparted"
}


select_gparted() {
	cat <<EOT
<!-- GParted message -->

<section>
	<header>$(_ 'Partitioning')</header>

	<div>
		<p>$(_ "On most used systems, the hard drive is already dedicated to \
partitions for Windows&trade;, or Linux, or another operating \
system. You'll need to resize these partitions in order to make space for \
SliTaz GNU/Linux. SliTaz will co-exist with other operating systems already \
installed on your hard drive.")</p>
	<p>$(_ "The amount of space needed depends on how much software you \
plan to install and how much space you require for users. It's conceivable \
that you could run a minimal SliTaz system in 300 megs or less, but 2 gigs \
is indeed more comfy.")</p>
	<p>$(_ "A separate home partition and a partition that will be used \
as Linux swap space may be created if needed. SliTaz detects and uses swap \
partitions automatically.")</p>
	<hr/>
	<p>$(_ "You can graphically manage your partitions with GParted. \
GParted is a partition editor for graphically managing your disk partitions. \
GParted allows you to create, destroy, resize and copy partitions without \
data loss.")</p>
	<p>$(_ "GParted supports ext2, ext3, ext4, linux swap, ntfs and \
fat32 filesystems right out of the box. Support for xjs, jfs, hfs and other \
filesystems is available as well but you first need to add drivers for these \
filesystems by installing the related packages xfsprogs, jfsutils, linux-hfs \
and so on.")</p>
	</div>

	<footer>
		<!-- Launch GParted -->
		<form>
			<button name="page" value="gparted" data-icon="hdd"
				title="$(_ 'Launch GParted, the partition editor tool')"
				>$(_ 'Execute GParted')</button>
		</form>
	</footer>
</section>

<h5>$(_ 'Continue installation')</h5>

<p>$(_ "Once you've made room for SliTaz on your drive, you should \
be able to continue installation.")</p>
EOT
}


#------------
# input page
#------------

select_source() {
	local media="$(/usr/sbin/tazinst get media "$INSTFILE")"
	local source="$(/usr/sbin/tazinst get source "$INSTFILE")"
	local list_media="$(/usr/sbin/tazinst list media)"
	local error

	# set default media
	[ "$media" ] || media="$(tazinst list media | cut -d ' ' -f1)"

	comment "Source selection"
	# cdrom
	if printf '%s' "$list_media" | grep -q "cdrom"; then
		input_media "cdrom" \
			"$media"
		label_media "cdrom" \
			"$(_ 'LiveCD')" \
			"$media" \
			"$(_ 'Use the SliTaz LiveCD')"
		br
	fi
	# usb
	if printf '%s' "$list_media" | grep -q "usb"; then
		input_media "usb" \
			"$media"
		label_media "usb" \
			"$(_ 'LiveUSB:')" \
			"$media" \
			"$(_ 'Enter the partition where SliTaz Live is located on your USB Key')"

		error="$?"
		select "$(/usr/sbin/tazinst list usb "$INSTFILE" | cut -d' ' -f2)" \
			"$source" \
			"SRC_USB"
		error_msg "$error" \
			"source" \
			2
		br
	fi
	# iso
	input_media "iso" \
		"$media"
	label_media "iso" \
		"$(_ 'ISO file:')" \
		"$media" \
		"$(_ 'Select a SliTaz ISO file located on a local disk')"
	error="$?"
	if [ "$media" == "iso" ]; then
		input "text" \
			"src_iso" \
			"$source" "" \
			"$(_ 'Select an ISO or enter the full path to the ISO file')"\
			"iso"
	else
		input "text" \
			"src_iso" \
			"" \
			"none" \
			"$(_ 'Select an ISO or enter the full path to the ISO file')"\
			"iso"
	fi
	datalist "$(/usr/sbin/tazinst list iso "$INSTFILE")" \
		"src_iso"
	error_msg "$error" \
		"source"
	br
	# web
	input_media "web" \
		"$media"
	label_media "web" \
		"$(_ 'Web:')" \
		"$media" \
		"$(_ 'Select a SliTaz version on the Web')"
	error="$?"

	if [ "$media" == "web" ]; then
		input "text" \
			"src_web" \
			"$source" "" \
			"$(_ 'Select a version or enter the full URL to an ISO file')"\
			"web"
	else
		input "text" \
			"src_web" \
			"" \
			"none" \
			"$(_ 'Select a version or enter the full URL to an ISO file')"\
			"web"
	fi
	datalist "$(/usr/sbin/tazinst help web "$INSTFILE")" \
		"src_web"
	error_msg "$error" \
		"source"
}

select_root_uuid()
{
	local root_uuid="$(/usr/sbin/tazinst get root_uuid "$INSTFILE")"
	local mode="$(/usr/sbin/tazinst get mode "$INSTFILE")"
	comment "root_uuid selection"
	if [ "$mode" == "upgrade" ]; then
		label "root_uuid" \
			"$(_ 'Existing SliTaz partition to upgrade:')" \
			"$(_ 'Specify the partition containing the system to upgrade')"
		error="$?"
	else
		label "root_uuid" \
			"$(_ 'Install SliTaz to partition:')" \
			"$(_ 'Specify the partition where to install SliTaz')"
		error="$?"
	fi
	select "$(/usr/sbin/tazinst list uuid "$INSTFILE")" \
		"$root_uuid" \
		"ROOT_UUID" \
		0
	error_msg "$error" \
		"root_uuid" \
		0
	br
}

select_root_format()
{
	local root_format="$(/usr/sbin/tazinst get root_format "$INSTFILE")"
	comment "root_format selection"
	format "$(/usr/sbin/tazinst list format "$INSTFILE")" \
		"$root_format" \
		"ROOT_FORMAT"
}

select_home_uuid() {
	local home_uuid="$(/usr/sbin/tazinst get home_uuid "$INSTFILE")"

	cat <<EOT
<!-- home_uuid selection -->

<fieldset>
	<legend>$(_ 'home partition')</legend>

	$(
	label "home_uuid" \
		"$(_ 'Separate partition for %s:' '/home')" \
		"$(_ 'Specify the partition containing %s' '/home')"
	select "$(/usr/sbin/tazinst list uuid "$INSTFILE")" \
		"$home_uuid" \
		"HOME_UUID" \
		0
	)
	<br/>
EOT
}

select_home_format()
{
	local home_format="$(/usr/sbin/tazinst get home_format "$INSTFILE")"

	comment "home_format selection"
	format "$(/usr/sbin/tazinst list format "$INSTFILE")" \
		"$home_format" \
		"HOME_FORMAT"
	cat <<EOT
</fieldset>
EOT
}


select_hostname() {
	local hostname="$(/usr/sbin/tazinst get hostname "$INSTFILE")" error

	cat <<EOT
<!-- hostname selection -->

<fieldset>
	<legend>$(_ 'Hostname')</legend>
	$(
	label "hostname" \
		"$(_ 'Set Hostname to:')" \
		"$(_ 'Hostname configuration allows you to specify the machine name')"
	error=$?
	input "text" \
		"HOSTNAME" \
		"$hostname" \
		"" \
		"$(_ 'Name of your system')"
	error_msg "$error" \
		"hostname" \
		2
	)
</fieldset>
EOT
}


select_root_pwd() {
	local root_pwd="$(/usr/sbin/tazinst get root_pwd "$INSTFILE")" error

	cat <<EOT
<!-- root_pwd selection -->

<fieldset>
	<legend>$(_ 'Root superuser')</legend>
	$(
	label "root_pwd" \
		"$(_ 'Root password:')" \
		"$(_ 'Enter the password for root')"
	error="$?"
	input "text" \
		"ROOT_PWD" \
		"$root_pwd" \
		"" \
		"$(_ 'Password of root')"
	error_msg "$error" \
		"root_pwd"
	)
</fieldset>
EOT
}


select_user_login() {
	local user_login="$(/usr/sbin/tazinst get user_login "$INSTFILE")" error

	cat <<EOT
<!-- user_login selection -->

<fieldset>
	<legend>$(_ 'User')</legend>
	$(
	label "user_login" \
		"$(_ 'User login:')" \
		"$(_ 'Enter the name of the first user')"
	error="$?"
	input "text" \
		"USER_LOGIN" \
		"$user_login" \
		"" \
		"$(_ 'Name of the first user')"
	error_msg "$error" \
		"user_login" \
		2
	)
	<br/>
EOT
}


select_user_pwd()
{
	local user_pwd="$(/usr/sbin/tazinst get user_pwd "$INSTFILE")" error

	label "user_pwd" \
		"$(_ 'User password:')" \
		"$(_ 'The password for default user')"
	error="$?"
	input "text" \
		"USER_PWD" \
		"$user_pwd" \
		"" \
		"$(_ 'Password of the first user')"
	error_msg "$error" \
		"user_pwd"
	cat <<EOT
</fieldset>
EOT
}


select_bootloader()
{
	local bootloader="$(/usr/sbin/tazinst get bootloader "$INSTFILE")" error

	cat <<EOT
<!-- bootloader selection -->

<fieldset>
	<legend>$(_ 'Bootloader')</legend>

	$(
	input "checkbox" \
		"bootloader" \
		"auto" \
		"$bootloader"
	label "bootloader" \
		"$(_ 'Install a bootloader.')" \
		"$(_ "Usually you should answer yes, unless you want to install \
a bootloader by hand yourself.")"
	error="$?"
	error_msg "$error" \
		"bootloader"
	)
	<br/>
EOT
}


select_winboot()
{
	local winboot="$(/usr/sbin/tazinst get winboot "$INSTFILE")" error

	comment "winboot selection"
	input "checkbox" \
		"winboot" \
		"auto" \
		"$winboot"
	label "winboot" \
		"$(_ 'Enable Windows Dual-Boot.')" \
		"$(_ "At start-up, you will be asked whether you want to boot \
into Windows&trade; or SliTaz GNU/Linux.")"
	error="$?"
	error_msg "$error" \
		"winboot"
	cat <<EOT
</fieldset>
EOT
}


errors_msg()
{
	if [ "$CHECK" ]; then
		echo '<span class="alert">'
		p "$(_ "Errors found. Please check your settings.")"
		echo '</span>'
	fi
}


select_settings() {
	local settings="$(/usr/sbin/tazinst get settings "$INSTFILE")"
	CHECK=$(GET CHECK)
	errors_msg

	cat<<EOT
<fieldset>
	<legend>$(_ 'Select source media:')</legend>

	<div class="media">$(select_source)</div>
</fieldset>


<fieldset>
	<legend>$(_ 'Select destination')</legend>

	<div>$(
		select_root_uuid
		printf '%s' "$settings" | grep -q "root_format" && select_root_format
	)</div>
</fieldset>


<fieldset id="options">
	<legend>$(_ 'Options')</legend>

	<div class="options">$(
	printf '%s' "$settings" | grep -q "home_uuid" && select_home_uuid
	printf '%s' "$settings" | grep -q "home_format" && select_home_format
	printf '%s' "$settings" | grep -q "hostname" && select_hostname
	printf '%s' "$settings" | grep -q "root_pwd" && select_root_pwd
	printf '%s' "$settings" | grep -q "user_login" && select_user_login
	printf '%s' "$settings" | grep -q "user_pwd" && select_user_pwd
	)</div>

	<div class="bootloader">$(
	printf '%s' "$settings" | grep -q "bootloader" && select_bootloader
	printf '%s' "$settings" | grep -q "winboot" && select_winboot
	)</div>
</fieldset>

<br/>
EOT
}


#--------------
# execute page
#--------------

save_settings()
{
	h5 "$(_ 'Checking settings...')"

	# install type
	/usr/sbin/tazinst set media "$(GET MEDIA)" "$INSTFILE"

	# source File
	case "$(/usr/sbin/tazinst get media "$INSTFILE")" in
		usb)
			/usr/sbin/tazinst set source "$(GET SRC_USB)" "$INSTFILE" ;;
		iso)
			/usr/sbin/tazinst set source "$(GET SRC_ISO)" "$INSTFILE" ;;
		web)
			/usr/sbin/tazinst set source "$(GET SRC_WEB)" "$INSTFILE" ;;
	esac

	# set defined url
	[ $(GET URL) ] && SRC_WEB=$(GET URL)

	# root Partition
	/usr/sbin/tazinst set root_uuid "$(GET ROOT_UUID)" "$INSTFILE"

	# format root partition
	[ "$(GET ROOT_FORMAT)" ] \
		&& /usr/sbin/tazinst set root_format "$(GET ROOT_FORMAT)" "$INSTFILE" \
		|| /usr/sbin/tazinst unset root_format  "$INSTFILE"

	# home Partition
	if [ "$(GET HOME_UUID)" ] ; then
		/usr/sbin/tazinst set home_uuid "$(GET HOME_UUID)" "$INSTFILE"
		[ "$(GET HOME_FORMAT)" ] \
			&& /usr/sbin/tazinst set home_format "$(GET HOME_FORMAT)" \
				"$INSTFILE" \
			|| /usr/sbin/tazinst unset home_format "$INSTFILE"
	else
		/usr/sbin/tazinst unset home_uuid "$INSTFILE"
		/usr/sbin/tazinst unset home_format "$INSTFILE"
	fi

	# hostname
	/usr/sbin/tazinst set hostname "$(GET HOSTNAME)" "$INSTFILE"

	# root pwd
	/usr/sbin/tazinst set root_pwd "$(GET ROOT_PWD)" "$INSTFILE"

	# user Login
	/usr/sbin/tazinst set user_login "$(GET USER_LOGIN)" "$INSTFILE"

	# user Pwd
	/usr/sbin/tazinst set user_pwd "$(GET USER_PWD)" "$INSTFILE"

	# win Dual-Boot
	/usr/sbin/tazinst set winboot "$(GET WINBOOT)" "$INSTFILE"

	# bootloader
	if [ "$(GET BOOTLOADER)" == "auto" ]; then
		/usr/sbin/tazinst set bootloader "auto" "$INSTFILE"
	else
		/usr/sbin/tazinst unset bootloader "$INSTFILE"
		/usr/sbin/tazinst unset winboot "$INSTFILE"
	fi
	input_hidden "CHECK" "yes"
}


tazinst_run()
{
	local mode="$(/usr/sbin/tazinst get mode "$INSTFILE")" error
	h4 "$(_ 'Proceeding to: %s' "$(gettext "$mode")")"
	/usr/sbin/tazinst execute "$INSTFILE" | /bin/busybox awk '{
		num=$1+0
		if (num>0 && num<=100){
			print "<script type=\"text/javascript\">"
			printf "document.write(\047<div id=\"progress\">"
			printf "<img src=\"/styles/default/images/loader.gif\" />"
			printf $1 "&#37; " substr($0, length($1)+2, 40)
			print "</div>\047)"
			print "</script>"
			}
		}'
	# end_of_install
	if /usr/sbin/tazinst log | grep -q "x-x-" ; then
		error=1
		echo "<script type=\"text/javascript\">"
		printf "document.write(\047<div id=\"progress\">"
		printf "<img src=\"/styles/default/images/stop.png\" />"
		_n 'Errors encountered.'
		printf "</div>\047)\n"
		echo "</script>"
		br
		br
		/usr/sbin/tazinst log | \
			/bin/busybox awk '$1 == "-x-x-",$1 == "x-x-x"' | sed 's/-x-x-/ /' \
			| grep -v "x-x-x"
	else
		error=0
		echo "<script type=\"text/javascript\">"
		printf "document.write(\047<div id=\"progress\">"
		printf "<img src=\"/styles/default/images/tux.png\" />"
		_n 'Process completed!'
		printf "</div>\047)\n"
		echo "</script>"
		br
		br
		br
		p $(_ "Installation is now finished, you can exit the installer \
or reboot on your new SliTaz GNU/Linux operating system.")
	fi
	return "$error"

}


tazinst_log()
{
	h4 "$(_ "Tazinst log")"
	printf '<pre>%s</pre>' "$(/usr/sbin/tazinst log | sed 's/\%/ percent/g')"
}


#-----------------
# page navigation
#-----------------

display_mode() {
	local mode="$(/usr/sbin/tazinst get mode "$INSTFILE")"
	case $mode in
		install)
			cat <<EOT
<h2>$(_ 'Install SliTaz')</h2>

<p>$(_ "You're going to install SliTaz on a partition of \
your hard disk drive. If you decide to format your HDD, all data will be \
lost. If you do not format, all data except for any existing /home \
directory will be removed (the home directory will be kept as is).")</p>
EOT
			;;
		upgrade)
			cat <<EOT
<h2>$(_ 'Upgrade SliTaz')</h2>

<p>$(_ "You're going to upgrade an already installed SliTaz \
system on your hard disk drive. Your /home /etc /var/www directories \
will be kept, all other directories will be removed. Any additional \
packages added to your old SliTaz system will be updated as long you \
have an active internet connection.")</p>
EOT
			;;
	esac
}


moveto_page()
{
	local back_page="$1" next_page="$2" back_msg next_msg

	case "$back_page" in
		partitioning)
			back_msg=$(_ 'Back to partitioning') ;;
		input)
			back_msg=$(_ 'Back to entering settings') ;;
		*)
			back_msg=$(_ 'Back to Installer Start Page') ;;
	esac

	case "$next_page" in
		execute|run)
			next_msg=$(_ 'Proceed to SliTaz installation') ;;
		reboot)
			next_msg=$(_ 'Installation complete. You can now restart') ;;
		failed)
			next_msg=$(_ 'Installation failed. See log') ;;
		input)
			next_msg=$(_ 'Continue installation.') ;;
		*)
			next_msg=$(_ 'Back to Installer Start Page') ;;
	esac

	cat <<EOT
<hr/>
<form>
	<button name="page" value="$back_page" data-icon="back" >$back_msg</button>
	<button name="page" value="$next_page" data-icon="start">$next_msg</button>
</form>
EOT
}


moveto_home() {
	cat <<EOT
<form>
	<button name="page" value="home" data-icon="back"
	>$(_ 'Back to Installer Start Page')</button>
</form>
EOT
}


page_redirection() {
	local page="$1"
	cat <<EOT
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>$(_ "A web page that points a browser to a different page after \
2 seconds")</title>
<meta http-equiv="refresh" content="0; URL=$SCRIPT_NAME?page=$1">
<meta name="keywords" content="automatic redirection">
</head>
<body>
<p>$(_ "If your browser doesn't automatically redirect within a few \
seconds, you may want to go there manually [here]" | \
sed "s|\[|<a href=\"?page=$page\">|; s|\]|</a>|")</p>
</body>
</html>
EOT
}


#----------
# checking
#----------

check_ressources() {
	local errorcode=0
	comment "check_ressources"
	if ! [ -x /usr/sbin/tazinst ] ; then
		h4 $(_ 'Tazinst Error')
		p $(_ '%s, the backend to %s is missing.' '<strong>tazinst</strong>' 'slitaz-installer';
		_ 'Any installation can not be done without %s.' 'tazinst')
		p $(_ "Check %s permissions, or reinstall the %s package." \
		'tazinst' 'slitaz-installer')
		errorcode=1
	else
		# check tazinst minimum version
		v=$(/usr/sbin/tazinst version | tr -d '[:alpha:]')
		r=$TAZINST_MINIMUM_VERSION
		if ! (printf '%s' "$v" | /bin/busybox awk -v r=$r \
				'{v=$v+0}{ if (v < r) exit 1}') ; then
			h4 $(_ 'Tazinst Error')
			p $(_ '%s, the %s backend, is not at the minimum required version.' \
			'<strong>tazinst</strong>' 'slitaz-installer';
			_ 'Any installation can not be done without %s.' 'tazinst')
			p $(_ 'Reinstall the %s package, or use %s in CLI mode.' \
			'slitaz-installer' 'tazinst')
			errorcode=1
		fi
		# check tazinst maximum version
		v=$(/usr/sbin/tazinst version | tr -d '[:alpha:]')
		r=$TAZINST_MAXIMUM_VERSION
		if ! (printf '%s' "$v" | /bin/busybox awk -v r=$r \
				'{v=$v+0}{ if (v > r) exit 1}') ; then
			h4 $(_ 'Tazinst Error')
			p $(_ "%s, the %s backend, is at a higher version than the maximum authorized \
by the %s." '<strong>tazinst</strong>' 'slitaz-installer' 'slitaz-installer';
			_ 'Any installation cannot be done.')
			p $(_ 'Reinstall the %s package, or use %s in CLI mode.' \
			'slitaz-installer' 'tazinst')
			errorcode=1
		fi
	fi
	return $errorcode
}


#---------------
# html snippets
#---------------

br() {
	echo '<br />'
}

hr() {
	echo '<hr />'
}

comment() {
	printf '<!-- %s -->\n' "$@"
}

a() {
	local page="$1" text="$2"
	printf '<a class="button" value="%s" href="?page=%s">%s</a>\n' \
		"$page" "$page" "$text"
}

button() {
	local action="$1" msg="$2" title="$3"
	printf '<a class="button" href="%s?page=%s" title="%s">%s</a>\n' \
		"$SCRIPT_NAME" "$action" "$title" "$msg"
}

open_div() {
	[ "$1" ] && printf '<div %s>\n' "$1" || echo '<div>'
}

close_div() {
	echo '</div>'
}

p() {
	printf '<p>%s</p>\n' "$@"
}

h4() {
	printf '<h4>%s</h4>\n' "$@"
}

h5() {
	printf '<h5>%s</h5>\n' "$@"
}

label() {
	local setting="$1" label="$2" title="$3" name="$4" error=0
	[ -z "$name" ] && name="$setting"
	printf '<label for="%s"' "$name"
	[ "$title" ] && printf ' title="%s">' "$title" || printf '%s' '>'
	# display label in red in case of error
	if [ "$CHECK" ]; then
		/usr/sbin/tazinst check "$setting" "$INSTFILE"
		error="$?"
		[ "$error" -gt "0" ] && [ "$error" -lt "127" ] && \
			printf '%s' '<span class="alert">'
		printf '%s' "$label"
		[ "$error" -gt "0" ] && [ "$error" -lt "127" ] && \
			printf '%s' "<sup>*</sup></span>"
	else
		printf '%s' "$label"
	fi
	echo '</label>'
	return "$error"
}


label_media() {
	local id="$1" label="$2" media="$3" title="$4" retcode=0
	if [ "$media" == "$id" ]; then
		label "source" \
			"$label" \
			"$title" \
			"$media"
		retcode="$?"
	else
		printf '<label for="%s"' "$id"
		[ "$title" ] && printf ' title="%s">' "$title" || echo '>'
		echo "$label</label>"
	fi
	return "$retcode"
}


error_msg() {
	local error="$1" setting="$2" line="$3"
	if [ "$CHECK" ]; then
		if [ "$error" -gt "0" ]; then
			[ "$error" -lt "128" ] && printf '%s' '<span class="alert">' \
				|| printf '%s' '<span class="warning">'
			if [ "$line" ]; then
				/usr/sbin/tazinst check "$setting" "$INSTFILE" 2>&1 | \
					/bin/busybox awk -v LINE="$line" '{if (NR==LINE){print}}'
			else
				/usr/sbin/tazinst check "$setting" "$INSTFILE" 2>&1
			fi
			echo '</span>'
		fi
	fi
}


select() {
	local list="$1" selected="$2" name="$3" type="$4"
	printf '%s' "$list" | \
		/bin/busybox awk -v SELECTED="$selected" -v NONE="$(_ 'None')" \
		-v NAME="$name" -v TYPE="$type" 'BEGIN{
		TYPE=TYPE+0
		print "<select name=\"" NAME "\">"
		print "<option value=>&lt; " NONE " &gt;</option>"
	}
	{
		printf "<option value=\"" $1 "\""
		if ($1 == SELECTED) printf " selected"
		if (TYPE == 0)
			print ">" $0 "</option>"
		if (TYPE == 1)
			print ">" substr($0,12) "</option>"
		if (TYPE == 2)
			print ">" $2 "</option>"
	}
	END{
		print "</select>"
	}'
}

input()
{
	local type="$1" name="$2" value="$3" selected="$4" help="$5" action="$6"
	printf '<input type="%s" id="%s" list="list_%s" ' "$type" "$name" "$name"
	printf 'name="%s" class="%s" ' "$(printf $name | tr [a-z] [A-Z])" "$type"
	[ "$value" ] && printf 'value="%s" ' "$value"
	[ "$value" == "$selected" ] && printf '%s' "checked "
	[ "$action" ] && printf \
		'onInput="document.getElementById(%s).checked = true;" ' "'$action'"
	[ "$help" ] && printf 'placeholder="%s" />\n' "$help" || echo "/>"
}

input_media()
{
	local id="$1" media="$2"
	printf '<input type="radio" name="MEDIA" value="%s" id="%s" ' "$id" "$id"
	[ "$media" == "$id" ] && echo 'checked />' || echo '/>'
}

input_hidden()
{
	local name="$1" value="$2"
	printf '<input type="hidden" name="%s" value="%s" />\n' "$name" "$value"
}

datalist()
{
	local list="$1" name="$2"
	printf '<datalist id="list_%s">\n' "$name"
	# workaround for browsers  that don’t support the datalist element..
	local script="displaySelValue(\"select_$name\",\"$name\")"
	printf '<select class="workaround" id="select_%s" ' "$name"
	printf "onChange='%s' onBlur='%s'>\n" "$script" "$script"

	# workaround ..end
	printf '%s' "$list" | \
		/bin/busybox awk -v NONE="$(_ 'None')" 'BEGIN{
		line=0
	}
	{
		TEXT=$1
		sub(".*/","",TEXT)
		printf "<option value=\"%s\">%s</option>\n", $1, TEXT
		line++
	}
	END{
		if (line < 1)
			printf "<option value=>&lt; %s &gt;</option>\n", NONE
	}'
	echo "</select>"
	echo "</datalist>"
}

format()
{
	list_fs="$1" selected="$2" name="$3" none="$(_ 'Do not format')"
	printf '<label for="%s" ' "$name"
	printf 'title="%s">' "$(_ "To format this partition, select a \
filesystem, usually it's safe to use ext4")"
	printf '%s</label>\n' "$(_ 'Formatting option:')"
	printf '%s' "$list_fs" | \
		/bin/busybox awk -v SELECTED=$selected -v NONE="$none" -v NAME="$name" '
BEGIN{
		RS=" "
		print "<select name=\"" NAME "\">"
		print "<option value=\"\">" NONE "</option>"
		line=0
	}
	{
		printf "<option value=\"" $1 "\""
		if ($1 == SELECTED) printf " selected"
		print ">" $0 "</option>"
		line++
	}
	END{
		if (line < 1)
			print "<option value=>< " NONE " ></option>"
		print "</select>"
	}'
}

form_start()
{
	printf '<form name="%s" method="get" ' "Form"
	printf 'onsubmit="return true" action="%s">\n' "$SCRIPT_NAME"
}

form_end()
{
	echo '</form>'
}

add_style()
{
	printf '<!-- add specific styles -->
<style type="text/css">
	section label {
		display:inline-block;
		vertical-align:middle;
	    width: 130px;
	}
	.media label {
		display:inline-block;
		vertical-align:middle;
	    width: 110px;
	}
	.options label {
		display:inline-block;
		vertical-align:middle;
	    width: 140px;
	}
	.text {
		width: 350px;
	}
	input {margin-bottom:3px;}
	span.alert {color: red}
	span.warning { color: darkgray}
	#progress {
		background-color: #f8f8f8;
		border: 1px solid #ddd;
		color: #666;
		cursor: progress;
		position: absolute;
		width: 348px;
		padding: 4px 4px 2px;
	}
</style>
<!-- workaround for browsers  that do not support the datalist element -->
<style type="text/css">
	.workaround {width: 110px;}
</style>
<script>
	function displaySelValue(selectId,inputId)
	{
		var slct = document.getElementById(selectId);
		var input = document.getElementById(inputId);
		document.getElementById("src_iso").value="";
		document.getElementById("src_web").value="";
		if (inputId =="src_iso"){
			document.getElementById("iso").checked = true;
		}
		if (inputId =="src_web"){
			document.getElementById("web").checked = true;
		}
		input.value = slct.options[slct.selectedIndex].value;
	}
</script>
<!-- datalist workaround end -->
\n'
}


#
# main
#

header

case "$(GET page)" in
	home)
		xhtml_header
		select_action
		select_install
		select_upgrade
		select_evaluate
		;;
	evaluate)
		xhtml_header
		select_evaluate
		;;
	install)
		xhtml_header
		/usr/sbin/tazinst set mode install "$INSTFILE"
		page_redirection partitioning
		;;
	partitioning)
		xhtml_header
		form_start
		display_mode
		select_gparted
		moveto_page home input
		form_end
		;;
	gparted)
		exec_gparted
		xhtml_header
		page_redirection partitioning
		;;
	upgrade)
		xhtml_header
		/usr/sbin/tazinst set mode upgrade "$INSTFILE"
		page_redirection input
		;;
	input)
		xhtml_header
		add_style
		form_start
		display_mode
		select_settings
		moveto_page home execute
		form_end
		;;
	execute)
		xhtml_header
		form_start
		display_mode
		save_settings
		if ! (/usr/sbin/tazinst check all $INSTFILE > /dev/null); then
			page_redirection "input&CHECK=yes"
		else
			tazinst_run && moveto_page home reboot \
						|| moveto_page input failed
		fi
		form_end
		;;
	reboot)
		/usr/sbin/tazinst clean "$INSTFILE"
		reboot ;;
	failed)
		xhtml_header
		form_start
		tazinst_log
		moveto_home
		form_end
		;;
	*)
		xhtml_header
		if check_ressources; then
			/usr/sbin/tazinst new "$INSTFILE"
			page_redirection home
		fi
		;;
esac

xhtml_footer

exit 0

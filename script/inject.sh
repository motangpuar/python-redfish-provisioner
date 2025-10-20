#!/bin/bash
# inject-kickstart.sh

ORIGINAL_ISO="/home/infidel/Downloads/rhel-9.5-x86_64-boot.iso"
OUTPUT_ISO="rhel-9.5-kickstart.iso"
HTTP_SERVER="192.168.8.75:3001"
KICKSTART_PATH="isos/kickstart/default.ks"

# Create working directory
WORK_DIR="/tmp/boot-iso-http"
mkdir -p $WORK_DIR

# Mount original ISO
mkdir /mnt/original
mount -o loop $ORIGINAL_ISO /mnt/original

# Copy only essential boot files (much smaller ISO)
cp -r /mnt/original/isolinux $WORK_DIR/
cp -r /mnt/original/images $WORK_DIR/
cp -r /mnt/original/EFI $WORK_DIR/
cp /mnt/original/.discinfo $WORK_DIR/ 2>/dev/null || true

umount /mnt/original

# Modify isolinux.cfg for BIOS boot
cat > $WORK_DIR/isolinux/isolinux.cfg << EOF
default vesamenu.c32
timeout 50
prompt 0

menu title RHEL Auto Install

label auto
  menu label ^Auto Install RT Worker
  menu default
  kernel vmlinuz
  append initrd=initrd.img inst.stage2=http://$HTTP_SERVER/isos/rhel/9.5 inst.ks=http://$HTTP_SERVER/$KICKSTART_PATH ip=dhcp quiet

label manual
  menu label ^Manual Install  
  kernel vmlinuz
  append initrd=initrd.img inst.stage2=http://$HTTP_SERVER/isos/rhel/9.5 ip=dhcp
EOF

# Modify grub.cfg for UEFI boot
cat > $WORK_DIR/EFI/BOOT/grub.cfg << EOF
set timeout=5
menuentry 'Auto Install RT Worker' {
  linuxefi /images/pxeboot/vmlinuz inst.stage2=http://$HTTP_SERVER/isos/rhel/9.5 inst.ks=http://$HTTP_SERVER/$KICKSTART_PATH ip=dhcp quiet
  initrdefi /images/pxeboot/initrd.img
}
menuentry 'Manual Install' {
  linuxefi /images/pxeboot/vmlinuz inst.stage2=http://$HTTP_SERVER/isos/rhel/9.5 ip=dhcp
  initrdefi /images/pxeboot/initrd.img
}
EOF

# Create the ISO
genisoimage -o $OUTPUT_ISO \
  -b isolinux/isolinux.bin -c isolinux/boot.cat \
  -no-emul-boot -boot-load-size 4 -boot-info-table \
  -eltorito-alt-boot -e images/efiboot.img -no-emul-boot \
  -J -R -V "RHEL HTTP KS" $WORK_DIR/

# Cleanup
rm -rf $WORK_DIR /mnt/original

echo "Created: $OUTPUT_ISO (HTTP kickstart: http://$HTTP_SERVER/$KICKSTART_PATH)"

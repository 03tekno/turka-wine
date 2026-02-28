#!/bin/bash

# Değişkenler
APP_NAME="turka-wine"
VERSION="1.0.0"
DEB_DIR="${APP_NAME}_${VERSION}_all"

echo "--- Paket oluşturma işlemi başlıyor ---"

# 1. Klasör Yapısını Oluştur
mkdir -p $DEB_DIR/DEBIAN
mkdir -p $DEB_DIR/usr/bin
mkdir -p $DEB_DIR/usr/share/$APP_NAME
mkdir -p $DEB_DIR/usr/share/applications
mkdir -p $DEB_DIR/usr/share/icons/hicolor/256x256/apps

# 2. Dosyaları Kopyala
cp turka-wine.py $DEB_DIR/usr/share/$APP_NAME/
cp icon.png $DEB_DIR/usr/share/icons/hicolor/256x256/apps/$APP_NAME.png

# 3. Çalıştırılabilir Script Oluştur (/usr/bin altına)
cat <<EOF > $DEB_DIR/usr/bin/$APP_NAME
#!/bin/bash
python3 /usr/share/$APP_NAME/turka-wine.py
EOF
chmod +x $DEB_DIR/usr/bin/$APP_NAME

# 4. Desktop Dosyası Oluştur (Menüde görünmesi için)
cat <<EOF > $DEB_DIR/usr/share/applications/$APP_NAME.desktop
[Desktop Entry]
Name=Turka Wine Yöneticisi
Comment=Wine ve Windows bileşenlerini kolayca kurun
Exec=$APP_NAME
Icon=$APP_NAME
Terminal=false
Type=Application
Categories=Utility;System;
EOF

# 5. Control Dosyası Oluştur (Paket bilgileri ve bağımlılıklar)
cat <<EOF > $DEB_DIR/DEBIAN/control
Package: $APP_NAME
Version: $VERSION
Architecture: all
Maintainer: Mobilturka
Depends: python3, python3-gi, libadwaita-1-0, gir1.2-adw-1, gir1.2-gtk-4.0
Description: Debian/Pardus için Wine yönetim ve kurulum aracı.
 Wine ve Winetricks kurulumlarını kolaylaştıran grafik arayüz.
EOF

# 6. Paketi Derle
dpkg-deb --build $DEB_DIR

echo "--- İşlem Tamamlandı! ---"
echo "Oluşturulan paket: ${DEB_DIR}.deb"
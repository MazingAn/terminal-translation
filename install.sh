echo 'install libs'
pip3 install requests
pip3 install colored
echo 'copy trans.py to /usr/local/share'
sudo cp trans.py /usr/local/share/
sudo cp trans.sh /usr/local/share/
echo 'add execute permission '
sudo chmod +x trans.py
echo 'ln to path /usr/local/bin'
sudo ln -s /usr/local/share/trans.sh /usr/local/bin/trans
echo 'SUCCESSFUL'
echo 'You can use trans'

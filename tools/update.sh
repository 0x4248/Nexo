
git pull
kill -9 $(ps -ef | grep 'python src/main.py' | grep -v grep | awk '{print $2}')
nohup python src/main.py > log.txt &
echo "Update completed and server restarted."
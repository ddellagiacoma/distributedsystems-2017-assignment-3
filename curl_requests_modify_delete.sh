curl -d 'entry=test' -X 'POST' 'http://10.1.0.1:80/board' & 
curl -d 'entry=testUpdated&delete=0' -X 'POST' 'http://10.1.0.2:80/board/001.1'

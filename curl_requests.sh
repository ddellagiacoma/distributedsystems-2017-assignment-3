for i in {1..40};
do
   curl -d 'entry=t1.' -X 'POST' 'http://10.1.0.1:80/board' &
   curl -d 'entry=t2.' -X 'POST' 'http://10.1.0.2:80/board' &
   curl -d 'entry=t3.' -X 'POST' 'http://10.1.0.3:80/board' &
   curl -d 'entry=t4.' -X 'POST' 'http://10.1.0.4:80/board' &
   curl -d 'entry=t5.' -X 'POST' 'http://10.1.0.5:80/board' &
   curl -d 'entry=t6.' -X 'POST' 'http://10.1.0.6:80/board' &
   curl -d 'entry=t7.' -X 'POST' 'http://10.1.0.7:80/board' &
   curl -d 'entry=t8.' -X 'POST' 'http://10.1.0.8:80/board'
done

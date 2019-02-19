g++ curl_multi.cpp -lcurl
rm /home/jerry/Desktop/for_quic/*
touch /home/jerry/Desktop/for_quic/log.txt
for i in {1..60};
do
    touch /home/jerry/Desktop/for_quic/$i
done

./a.out

# Tugas Besar 2 IF3130 - Jaringan Komputer
> Implementasi protokol TCP-like Go-Back-N

## Anggota Kelompok
NIM      | Nama
---      | ----
13520094 | Saul Sayers
13520115 | Maria Khelli
13520151 | Rizky Ramadhana Putra Kusuma

## Spesifikasi Tugas
Anda diminta untuk membuat sistem program yang terdiri dari server dan client yang berkomunikasi lewat jaringan. Program **wajib** ditulis dalam **Python 3**.

Program mengikuti spesifikasi sebagai berikut:
1. Server dan client berkomunikasi menggunakan socket dengan protokol UDP.
2. Client melakukan pencarian server dengan mengirim request di broadcast address.
3. Data yang akan dikirim tidak memiliki batasan tipe file / “ekstensi” (.zip, .md, .exe, .txt, etc) / tipe file. Lakukan pengiriman secara raw binary untuk menghindari file corrupt.
4. Gunakan asumsi berikut ketika membuat bagian pengiriman segmen program : Pengiriman paket melewati channel yang tidak reliable, paket dapat hilang, duplikat, korup, dan masalah-masalah lain.
5. Sebelum pengiriman, server akan melakukan three way handshake dengan client. Usahakan sesuai dengan spesifikasi three way handshake yang ada pada IETF, mencakup spesifikasi three-way-handshake Syn - Syn Ack - Ack. Berhasilnya three way handshake menandai koneksi antara server-client telah ter-establish. Jika terjadi kegagalan pengiriman paket karena suatu alasan, error handling behaviour program dibebaskan.
6. Ketika server dijalankan, server akan memasuki kondisi idle dan mendengarkan request client dari broadcast address. Apabila server mendapatkan request client, server akan menyimpan address client ke dalam list. Setiap server mendapatkan client, server akan memberikan prompt ke pengguna untuk melanjutkan listening atau tidak. Apabila tidak, maka server akan mulai mengirimkan berkas secara sekuensial ke semua client yang terdapat dalam list. Berikut adalah contoh eksekusi server

## Daftar Requirement
* Python 3

## Cara Menjalankan Program
Buka 2 terminal untuk masing-masing client dan server lalu jalankan kedua command di bawah pada terminal.

```bash
python server.py -b [broadcast port] -f [path file input] -cp -tp
```

```bash
python client.py -c [client port] -b [broadcast port] -f [path output]
```

**Keterangan Flags**:
1. -b : Diisi port untuk broadcast server. Defaultnya adalah 8080.
2. -c : Diisi port untuk client server. Defaultnya adalah 3000.
3. -f : Diisi path menuju file dari root repository. Untuk server, defaultnya adalah server_files/git.exe
4. -cp : Merupakan flag tanpa parameter yang digunakan untuk mengaktifkan **BONUS** Paralelisasi pada program server. Defaultnya adalah False.
5. -tp : Merupakan flag tanpa parameter yang digunakan untuk mengoptimasi pengiriman dengan threads (memisahkan listening dan sending data agar concurrent). Defaultnya adalah false.

**NOTE**: Apabila flag -f tidak diisi, maka program akan secara otomatis memberikan name file tersebut dengan nama dan extension aslinya melalui Bonus Metadata. **Disarankan** untuk hanya menggunakan salah satu dari flag -cp atau -tp untuk sekali menjalankan programnya.

## Alur Program
Setelah menjalankan server akan keluar output sebagai berikut:
```
[!] Server started at localhost:8070
[!] Source File | git.exe | 45584 bytes      
[!] Listening to broadcast address for clients.
```

Setelah menjalankan client akan keluar output sebagai berikut:
```
[!] Client started at localhost:3001
[!] [Handshake] Initiating three way handshake...
```

Server akan mengeluarkan prompt sebagai berikut:
```
[!] Received request from 127.0.0.1:3001     
[?] Listen more? (y/n) 
```

Apabila memberikan input y, maka program akan menunggu mendengarkan inisiasi handshake dari client lain. Apabila memberikan input N, maka program akan segera membalas pesan Syn untuk tiap clientnya. 

**NOTE**: Dengan flag -cp, maka client baru tidak perlu menunggu server memberikan input y. Client - client baru dapat muncul bersamaan dan terdeteksi oleh server kemudian dimasukkan queue, sehingga tidak perlu sekuensial client1 - y - client2 - y - client3 - n dsb.


Berikut adalah output dari server dan client saat melakukan inisiasi transfer file:
```
!] Received request from 127.0.0.1:3001     
[?] Listen more? (y/n) n

Client list:
1. 127.0.0.1:3001

[!] Commencing file transfer...
[!] [Handshake] Handshake to client 1...     
[!] [Handshake] Sending SYN ACK to client    
[!] [Handshake] Received ACK from client, handshake success!
[!] [Client 1] Initiating file transfer...   
[!] [Client 1] [Metadata] Sent
[!] [Client 1] [Metadata] [ACK] Segment acked
[!] [Client 1] [Num=1] Sent
[!] [Client 1] [Num=2] Sent
[!] [Client 1] [Num=1] [ACK] Segment acked   
[!] [Client 1] [Num=2] [ACK] Segment acked   
[!] [Client 1] [FIN] Sending FIN .....       
[!] [Client 1] [FIN] Acked
```

Dan berikut adalah output dari client saat menerima file dari server:
```
[!] [Handshake] Received SYN ACK from server 
[!] [Handshake] Sending ACK to server...     
[!] [Client] [Metadata] Received Metadata    
[!] [Client] [Metadata] Filename: git | Extension: .exe
[!] [Client] [Num=1] Received Segment        
[!] [Client] [Num=2] Received Segment 
```


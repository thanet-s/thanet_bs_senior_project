# การศึกษาเปรียบเทียบประสิทธิภาพระหว่างระบบที่พัฒนาแบบโมโนลิธ และ ไมโครเซอร์วิสโดยใช้ระบบจัดการฐานข้อมูลแบบกระจายติดตั้งบนระบบจัดการคอนเทนเนอร์


## ข้อมูลโครงการ

อาจารย์ที่ปรึกษา
- อ.วาโย ปุยะติ

สามาชิก
- นายธเนษฐ ศิริบูรณ์

## สถาปัตยกรรม
- KVM
- Docker
- Kubernetes
- FastAPI
- CockroachDB
- NGINX
- Ansible

# How run backend app on local machine (dev & test)

## Prerequisite

### Running machine
- OS: Linux, MacOS, Windows
- Softwate: Docker, Docker Compose, Git

### App
- [Monolithic](src/monolithic/)
- [Microservice](src/microservice/)

# How to deploy project to host and loadtest (full loadtest)

## Prerequisite
### Server
- CPU: x86_64 with Intel VT-x or AMD-V 4 core/ 8 SMT thread or above
- RAM: 32 GB
- DISK: 256 GB or above
- NIC: 1 Gbe RJ45 port or above
- OS: Ubuntu 22.04.xx Server from [https://releases.ubuntu.com/jammy/](https://releases.ubuntu.com/jammy/)
- Additional: Set IP address to 192.168.1.100 and able to connect via ssh with password

** you can adjust VM memory for low memory machine by follow [docs/Adjust_VM_memory.md](docs/Adjust_VM_memory.md)

### Network router
- IP: 192.168.1.1
- Subnet: 255.255.255.0
- LAN port: 1 Gbe or above
- Additional: Internet connection

### Client machine
- CPU: x86_64, ARM64
- OS: Linux, MacOS, Windows Subsystem for Linux for Windows
- Softwate: Docker, Docker Compose, Git
- NIC: 1 Gbe RJ45 port or above
- Additional: Set static IP address to same server network

## Deployment step
- Clone git project to Client machine
- Open this project in Terminal
```
cd /<PATH>/<TO>/<THIS_GIT_DIR>
```
- Clone Kubespray
```
git clone https://github.com/kubernetes-sigs/kubespray.git devops/deploy/kubespray --branch v2.21.0
```
- [OMG opensource!!] Fix Kubespray bug by remove some commit & cherry-pick new PR
```
git -C devops/deploy/kubespray rebase -r --onto d919c58e21a8693bd3d1aab3a963947a87986053^ d919c58e21a8693bd3d1aab3a963947a87986053 && \
git -C devops/deploy/kubespray cherry-pick \
    5fbbcedebcf4c147ec3c94d51c328442a45fef4e \
    919e666fb93879795594bfccdc36cfbbda198335 \
    0707c8ea6f17250b67bdb397fac1f3abd8263da0 \
    145c80e9abd7e740733cb716ddc30ef122711cd1 \
    1d9502e01d39c8111e2ad09f22ef025c0e89e284 \
    36c6de9abdcb1ff2ae0e105110be703cae21a956 \
    3c2eb5282864b23a0a878de7460967629f037081 \
    fa92d9c0e99c06815a3af518347ee682ecbf2c98 \
    75b07ad40c1da804a32842b6cc72aa551d23dd13 \
    d908e86590f0dba57027bcc351e7665b4646358f \
    f366863a9911e6575462eedca4fba04c60beb72e \
    b7fe3684695db6a64fe371794cc94b1bc020bfab
```
- Prepare docker image
```
docker build -t project-utils devops && docker build -t kubespray devops/deploy/kubespray
```
- Run setup server playbook by enter Ubuntu 22.04 server user & password
```
chmod +x devops/deploy/*.sh && ./devops/deploy/deploy.sh
```

## Loadtest step

- Run loadtest scripts
```
chmod +x devops/loadtest/*.sh && ./devops/loadtest/loadtest.sh
```
- View result in "loadtest_result" directory
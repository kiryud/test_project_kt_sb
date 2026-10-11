# 백엔드에 대한 지식 정리

## Q.서버가 무엇인지 알려면 뭘 알아야할까?

> 요약하면 소규모 프로젝트면 웹서버, 웹 애플리케이션 서버, DBMS의 간단한 구조를 docker-compose로 관리 가능하게 만드는 것으로 충분하다
> 물론 나에겐 부족하기에 최대한 여러 요소가 한눈에 들어오게 다시 정리하고자 한다

### 1. 컴퓨터와 네트워크에 대해 짤막하게 짚고 넘어가야 할 것 같다
- 데스크탑(과 노트북), 모바일 기기로 구분 가능한 단말(`terminal`)을 먼저 알아야 한다
    - linux에서 cli 환경을 사용할 수 있게 제공해주는 `terminal`이라는 프로그램의 어원이기도 하다
- 그 다음 각 단말들이 서로 통신하는 방법인 소켓(`socket`)과 네트워크(`network`)에 대해 이해하면 될 것 같다
- 마지막으로 이 환경에서 통신을 위한 규약(`protocol`)에 대해 이해하면 될 것 같다


### 2. 통신 방법을 알아야한다
- OSI 7계층과 TCP/IP 4계층에 대해 자세하게 알 필요가 존재하지 않는다
    - 두 영역 모두 클라이언트측에서도 동일한 물리 계층을 가진다는 부분을 생략해서 표현하기 때문에 더 로우레벨의 내용을 다루는 지금은 필요한 부분만 확인하도록 하자
    - 42 공통과정 진행 중 OSI를 깊게 팔 필요가 없다 (TCP/IP 4계층만으로도 충분하다)
    - 실질적으로 알아야 하는 것은 `socket`기반 통신을 한다는 사실과 그 방법을 이해하는 것에 있다
- OSI의 제 4계층이면서 TCP/IP 제 3계층인 전송 계층은 이런 함수를 기반으로 작동한다 
    - `TCP`
        - `socket` `bind` `listen` `accept` `close` | `connect`
        - I/O 이벤트 통지 및 처리 모델
            - 준비 완료 통지(Readiness): `select` -> `poll` -> `epoll(Linux)` / `kqueue(BSD, macOS)`
            - 작업 완료 통지(Completion, 커널이 직접 I/O 수행): `IOCP(Windows)` -> `io_uring(Linux 최신)`
        - `send` `recv`
    -  `UDP`
        - `socket` `bind` `close` | `connect`
        - `sendto` `recvfrom`
        > udp는 비연결지향이라서 클라이언트는 `bind` 없이 `sendto`, 서버는 `bind` 후 `recvfrom` 을 통해 통신한다
- 그 윗계층인 응용계층은 굉장히 많은 것이 있지만 (전송계층이 아닌 모든 프로토콜이 이곳에 속한다) 당장 알아둬야하는 것은 세가지 밖에 없다
    - `http/https`
        - web/app 공용 프로토콜
        - `websocket` http api를 통해 만들어진 연결 유지용 프로토콜 `ws/wss`로 주소가 시작한다
            - 새로운 프로토콜의 표준을 만들어 호환성 없는 무언가를 만들 필요 없이 진입점으로 http api를 사용하며 그 이후 해당 TCP 소켓에서 양방향 통신을 한다
        - `https/wss`는 `http/ws`에서 `tls/ssl`을 통해 보안을 강화한 프로토콜이다
            - `web server`에서 해당 보안 연결을 처리해 그 이후에 있는 서버의 부담을 줄이는 구조로 사용하며 nginx에선 listen내부에서 관리할 수 있다
            - `tls`은 1999년 표준화 기구 `IETF`로 이관되어 새로 정의된 이름이다
            - `ssl`이라는 기능이 변화한 것이 아니라 nginx의 config file에서 ssl로 시작하는 설정을 그대로 사용한다
            - brew나 다른 패키지 매니저에서 설치되는 ca_certificates 패키지가 해당 프로토콜에서 사용되는 인증서를 관리해준다
                - 인증서 관리 업체에 따라 신뢰도가 다르고 서비스를 판매하고자 한다면 대가를 지불하는것이 좋은 선택이다
    - `irc`
        - ft_irc(가 남아있을지는 모르지만)
        - irc는 RFC문서를 기반으로 그 구성을 파악할 수 있지만 기본적인 명령어를 위한 정보조차 완전하지 못하다
            - 과제 진행중에 내 깃헙을 보면 안되는 이유이기도 하다 (나는 범위 내에서 모든 case와 numeric reply message를 완벽하게 정리했거든)
            - `tcpflow`를 통한 적극적인 리버스 엔지니어링을 추천한다
    - `ssh`
        - `ecole 42`의 `piscine`을 했다면 `ssh-keygen` 및 공개 키 등록을 모를 수 없지
        - ip를 알고 있는 로컬 네트워크의 다른 기기 접속도 가능하다
        - 학생이라면 혜택을 주는 `termius`를 통해 간편하게 집에 있는 개발용 메인 pc에 접속하여 과제를 진행할 수도 있다 (물론 밖에서 집에 있는 pc에 remote로 접속하고싶지 않겠지만)
        - `ssh`를 통해 접근한 계정은 id과 pw를 통해 정상적으로 로그인하더라도 `remote` 환경으로서 로컬 환경보다 더 적은 권한만 허용되어있고 그렇게 제약이 존재하는 상태를 유지하는 것이 옳다
        - 공용 컴퓨터에서 본인 github repository를 지키고 싶다면 `~/.ssh`에 `config` 파일을 만들어 Host를 설정해 본인의 키를 활용하도록 명시해둬야한다 ([방법](https://github.com/kiryud/dl_3_1_flutter/blob/main/vault/git_something/how_to_use_Git_and_Github_in_Window.md)) 


## 백엔드 서버의 구성과 종류

1. 서버의 물리적 위치에 따라 분류
    - `on-premise`
        - 쉽게 말하면 물리 서버라고 할 수 있다
        -  데이터 센터 규모를 가진 기업도 있지만 서버실을 운영하는 기업도 있고 개인 서버렉을 가진 개인([서울리안](https://www.youtube.com/watch?v=25xYwTFJQxw&list=PLTJcpVY_0CL2FvpFwaEyqGLVEA-Xiz49X&index=4))도 있다
    - `off-premise`
        - 클라우드 서버이다

2. 아키텍쳐에 따른 분류
    - `monolithic`
        - 5 circle 과제 `Inception`이 해당 아키텍쳐 기반의 웹 서버를 구성하는 과제이다
        - `docker-compose.yml` `Dockerfile` `Makefile` `.env`를 통해 구성된다
            - 자명한 사실이지만 `.env`는 깃허브에 절대 올리면 안된다.
                - (근데 과제 수준에서 딱히 꼭 기밀을 유지해야할 api key같은 데이터 없길래 걍 올려둠)
        - 각 컨테이너는 필요에 따라 여러 파일을 추가로 가질 수 있다
            - `nginx` : `*.conf`
            - `word press` : `init.sh`
            - `mariadb` : `init.sql`
    - `modular monolithic`
        - 같은 데이터베이스를 공유할 필요가 없는 서비스를 분리한 구조
        - 모듈 단위로 데이터베이스가 분리된 형태이다
        - 당연히 모듈의 경계는 상황마다, 사람마다, 기업마다, 환경마다 다 다르지만 기본적으로 해당 환경에 적합한 구성을 만들기 위해 노력한다
    - `microservices`
        - 서비스를 기준으로 모든 서비스 서버가 분리되어있고 개별적인 데이터베이스를 가지고 각자 다른 DBMS를 활용하는 것 까지 가능하다 (그렇다고 rdbms를 종류별로 다르게 쓰라는 의미가 아니다)
        - 당연히 `container`가 없으면 MSA는 사실상 없다고 봐도 된다. 그건 사람이 할 일이 아님;;

3. 서비스에 따른 분류
    - `webserver`
    - `web application server`
    - `database management system server`
    - 그 외에도 분리된 역할에 따른 여러 서버가 존재한다
        - `s3` `bucket`으로 널리 알려진 `CDN` 서버도 있다 (비용이 있기때문에 섣부른 사용은 지양하자)


## container

> `docker` `docker compose` `kubernetes` (사라진 ft_container라는 과제는 이쪽이 아니라 C++ STL 이야기다)
> 물론 쿠버네티스는 container를 관리하는 pod 단위에서 작동하는 프로그램이다 (그래서 훨씬 어렵다)

- `container`란 6가지 `name space`와 `cgroup`을 기반으로 만들어진 격리된 공간을 말한다.
    - `pid` : 프로세스 ID, Dockerfile의 exec `entrypoint` `cmd`에서 시작한 프로세스들의 pid가 1이 된다
    - `net` : 네트워크, vm에서 포트포워딩을 하거나 container에선 `host_port:container_port` 설정을 할 때 자연스럽게 보게 된다
    - `mnt` : linux file system에서 `/` 이전으로 갈 수 없다는걸 통해 특정 directory를 root directory로 만들어 격리한다 (사실 초기 명령어 `chroot`는 경로 요청으로 뚫리는 버그가... 그래서 `pivot_root`가 나왔다)
    - `ipc` : 프로세스 간 통신에서 사용되는 공유 자원을 격리할 수 있다
    - `uts` : 호스트 이름 (`hostnamectl`로 확인할 수 있는 그 이름)
    - `user` : 사용자(`UID`), 그룹(`GID`)의 권한 관리
    - `cgroup`은 namespace로 격리된 프로세스들이 사용할 수 있는 자원을 제한하는 기술이다 (이걸 돈 받고 파는게 cloud server) (llm, 기계학습쪽에선 gpu 빌려쓰기로도 잘 알려져 있다)

> `mount` : USB나 외장 하드 연결했을때 사용할 수 있게 해주는 그 기능이다
> `ipc` : `pipex`를 평가하거나 선택하면 한번쯤은 설명을 듣거나 하게 될 내용이다


- `docker`는 `container`를 생성, 실행 및 관리를 해주는 프로그램이다
    - `Dockerfile` : 도커 이미지를 만들기 위한 설계도 
    - `docker image` : 도커 컨테이너를 원하는 만큼 생성할 수 있는 원본
    - `docker container` : 자원을 할당받아 작동중인 하나의 격리된 프로세스
    - `docker volume` : 격리된 환경에서 여러 컨테이너에서 공유해야하거나 컨테이너에 문제가 생겨도 저장해야하는 파일을 위한 공간
    - `docker network` : 각 컨테이너가 호스트 기기의 어떤 네트워크 자원(포트)을 점유하는지와 각자 어떻게 서로 통신 가능한지, 어떤 컨테이너끼리 통신할 수 있을지 설정
- `docker compose`는 길고 복잡한 여러 줄에 걸친 명령어를 `docker-compose.yml`을 통해 관리하는 프로그램이다
    - `.env`를 통해 공통 환경변수 세팅이 가능하다
    - `volume` : 간단하게 관리 가능해졌다 (이제 컨테이너 하나하나 마운트 시켜주지 않아도 된다)
    - `network` : 마찬가지로 직접 연결하지 않고 어떤 구성인지 정의만 하면 된다
    - `depends_on` : 컨테이너의 시작 순서를 명시한다 ('시작 순서'라고 된 이유가 있다...)
    - `healthcheck` : 컨테이너의 상태를 확인해준다 (depends_on과 달리 제대로 서버가 켜졌는지 확인할 수 있다)
    - 더 많은 기능이 있지만 배움이 충분치 않아 잘 모르는 영역이 많다

- `kubernetes`는 여러개의 `container`를 가진 `pod` 단위로 동작 가능하다
    - 당장 내가 학습하지 않은 영역이라 자세하게 알지 못하는 영역
    - 다만 대부분의 경우 쿠버네티스가 필요할 정도로 큰 서버가 필요하지 않아 `docker compose`로 충분하다고 한다

## 백엔드 언어 / 라이브러리 / 프레임워크

### 언어 / 라이브러리 / 프레임워크


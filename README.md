# kotlin spring boot test project

## sequence

- github repository 생성
- architecture 설계
- tech 결정
- 결정된 tech를 기반으로 gitignore 제작
    - [gitignore.io](https://www.toptal.com/developers/gitignore)

- backend tool 추가
    - 활용 가능한 api document service
        - swagger
        - apidoc

- `docker-compose.yml` 제작
    - container
        - nginx
            - config (*.conf)
        - frontend (null)
        - backend (spring boot)
        - dbms
            - mariadb
    - network
    - volume
    - dependency
    - health-check
    - env

- `Makefile` 제작
    - CI CD를 위한 도구에 익숙하지 않아 단순히 환경변수와 명령어를 통일시키려는 목적

- `init.py`와 `.env.example`을 통한 `.env` 파일 생성
    - 최소한도의 기능과 보안을 가진 최소한도의 정책
    - default값을 채워주는 형태이지 난수 생성은 없다

- deployment
    - 미정

### nginx

- *.conf
    - listen
    - server name
    - root
    - index
    - log (access_log, error_log)
    - ssl (ssl_protocols, ssl_certificate, ssl_certificate_key)
    - location
        - try_files
        - proxy_pass
        - proxy_http_version
        - proxy_set_header
        - proxy_set_header Upgrade
        - proxy_set_header Connection
        - proxy_set_header Accept-Encoding

- ssl은 더이상 사용하면 안된다. tls에서도 v1.2, v1.3을 써야한다
    - [지원 중지 권고](#tls)

- zero-copy를 통해 정적 파일을 유저모드에서의 메모리를 건너뛰고 커널모드에서 전송할 수 있다
    - http에선 잘 되었는데 https부턴 암호화가 강제되어 sendfile이 커널에서 처리되지 못함
        - 암호화를 유저 모드의 메모리에 복사해서 진행 후 전송해야했음
    - kTLS(kernel TLS)을 통해 https에서도 최대한 커널모드를 유지할 수 있게 되었다
        - `ssl_conf_command Options KTLS;`을 명시해 활성화
        - Linux Kernel 4.13+, OpenSSL 3.0+, nginx의 합작
            - 이 버전은 TLSv1.2만 지원 가능해서 TLSv1.3을 위해선 Linux Kernel 5.2+ 필요
            - 사용할 nginx의 이미지에서 각 버전이 어떻게 구성되어있는지 잘 살펴야할 것 같다
        - TLS handshake만 user mode의 OpenSSL에서 처리하고 session key(대칭키임) Linux kernel socket에게 넘겨줌
            - 이때 사용 가능한 대칭키 암호화 알고리즘을 명확히 알고 사용해야한다
        - nginx가 정적 파일을 sendfile할 때 kernel 혹은 network card HW에서 넘겨받은 session key로 암호화
            - TLS Device Offload를 지원하는 NIC로 kTLS를 활성화 하는 경우 `TLS_TX_ZEROCOPY_RO`라는 커널 내부 복사도 최적화 할 수 있는 옵션이 있다
                - 물리적인 기기인만큼 어떤 버전의 TLS를 처리할 수 있는지는 쓸 기회가 생길 때 다시 알아보면 될 듯 하다
        - Linux Kernel의 특정 버전의 이상을 요구하는 부분을 보면 알겠지만 Host의 kernel을 사용하는 container의 경우 Host의 kernel에서 지원하지 않거나 지원하더라도 설정이 되어있지 않는다면 container 내부의 설정만으로는 사용할 수 없다

#### 인증서 관리
- ca_certificate
    - 내 프로젝트와 별개로 시스템에 설치된 root ca public key 목록
- letsencrypt
    - 90일 무료 인증서 발급 기관
- certbot
    - 만료 30일 전 갱신 봇

### DBMS

#### H2
- 메모리 상의 가상 dbms

#### redis
- in memory, nosql db

#### postgres
- 기본적인 사용은 RDBMS의 공통적인 사용법과 같다
- 부가 기능이 굉장히 많은데 아직 학습하진 못했다

#### supabase
- postgres 기반의 Backend as a Service


#### mariadb

> docker 이미지 있으니 걍 쓰는중

- docker compose를 통해 실행 및 관리
    - 환경변수 없이 임시 값 넣어둔 상태
    - 다른 환경변수까지 정리된 후 .env를 사용하도록 수정 예정
- init.sql을 통해 데이터베이스, 테이블 생성 및 초기화

### spring boot (kotlin)

> 버전은 설계 완성 후 프로젝트 시작시 제대로 고정할 예정
> 당장은 특정 버전을 사용해야하는 이유에 대한 고민이 존재하지 않는 상태이다

- [Spring Initializr](https://start.spring.io/)를 활용한 프로젝트 생성
    - dependencies
        - spring web
            - servlet 기반
        - spring security
            - default로 서버 접근시 로그인 페이지로 링크, user와 실행시 나오는 비밀번호로 로그인 가능
            - 최신 버전에서는 WebSecurityConfigurerAdapter를 상속받지 않음
            - SecurityConfig (이름은 중요하지 않음) class 제작
                - @Configuration
                - @EnableWebSecurity
                - SecurityFilterChain 메서드를 @Bean으로 등록하여 URL별 권한 제어 및 보안 설정
        - spring data jpa
            - dbms와의 연동 필요. H2를 사용하다가 mariadb를 사용하도록 변경 가능
            - 이니셜라이저를 통해 `build.gradle.kts`에 작성되어있음
            - application.yml에서 dbms 정보를 설정
        - mariadb driver
    - build
        - spring boot 4.x.x 이상의 release
        - JAVA 21 이상
        - gradle kotlin

- `swagger` 연동

```build.gradle.kts
dependencies{
	// Swagger (OpenAPI) 버전은 프로젝트의 환경에 맞추면 된다
	implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.8.0")
}
```

- 테스트
    - `WebMvcTest`
        - 기본적으로 포함된 `spring-boot-starter-webmvc-test`를 통해 테스트 가능

- 레이어드 아키텍처
    - controller - service - repository
    - 이 경우 spring boot라서 adapter를 작성할 필요는 없다

- 헥사고날 아키텍처
    - port와 adapter를 기반으로 결합도를 낮춰 더 유연한 개발이 가능해짐

```md
controller
service
repository
```

- controller의 역할과 책임
    - request body
    - query parameter
    - path variable
    - response body

- service의 역할과 책임
    - user의 권한에 따라 요청된 비즈니스 로직을 실행


- repository의 역할과 책임
    - JPA(ORM)을 통해 어떻게 DBMS와 소통할지 선언
    - ORM에서 최종적으로 어떤 SQL을 만드는지 확인해 N+1같은 널리 알려진 문제는 미리 잡아야 한다

```md
dto
entity
```

- dto의 역할과 책임
    - data 전송 객체로서 필요한 범위의 data를 저장 가능해야한다
    - 불필요한 정보는 빈 공간으로 둘 수 있어야한다

- request dto의 역할과 책임
    - 요청을 받을 때 오는 정보를 관리할 수 있어야한다
    - 정보를 관리하면서 생기는 다른 정보도 관리 가능해야한다

- response dto의 역할과 책임
    - 반환을 위한 정보를 다룰 수 있어야한다
    - 비즈니스 로직의 동작에 따른 data의 crud가 가능해야한다
    - api의 반환값을 더 쉽게 만들 수 있도록 잘 설계되어있어야한다

- entity의 역할과 책임
    - 일단 지금 수준에선 db의 table과 일치해야한다
    - ORM에서 가져오는게 전용 dto로 갈 예정이라 사실상 Create나 Update를 요청할 때 사용하게 될 듯 하다

#### service 구현
- service에서 제공하는 기능 정리
- table(entity) 정의 및 구현
- dto, repository 정의 및 구현
- controller, service 정의 및 구현

#### user service 구현
- user service의 기능 정리
- user table 구현
    - [UUID](#uuid)란?
    - UUID와 auto increment를 모두 사용해야하나?
        - 내부적으로는 indexing하기 좋은 auto increment인 정수를 사용하는것이 좋고 외부에 공개하는 유저 식별자는 UUID로 하는것이 좋다
        - RESTful api를 지향한다면 UUID를 resource-id로 사용하게 된다
            - UUIDv7는 첫 영역이 timestamp라서 등록 순서대로 정렬된다
                - B+Tree기반의 index에 굉장히 좋다
                - 해당 UUID의 생성 일시가 그대로 노출된다
                - UUID만으로 indexing이 되어 auto increment가 불필요해 보이지만 이 때에도 sequence의 역할을 해줄 수 있다
                    - timestamp는 발급 당시 기기의 설정에 종속되어있다
            - UUIDv4는 임의의 난수로서 예측이 불가능하다 (굉장히 낮은 확률로 겹칠 수는 있다)
                - 이 때 내부 index로 auto increment인 정수를 사용하면 좋다 
    - 어떤 값이 PK가 되어야하는가
        - 어차피 키를 하나만 쓸것도 아니라 제 3의 값도 테이블 구성에 따라 키가 될 수 있는거라 유저서비스를 위한 정보가 어떻게 구성될지가 중요할 듯 하다
        - 중복 안되는 정보가 한두개가 아니다
    - 어떤 정보를 가져야하나
        - login(signin), signup page에서 받을 정보
            - 개인정보 정책과 연동되는 부분
            - 비밀번호는 반드시 해시로 저장되어야 한다 (`BCryptPasswordEncoder` 사용하도록 제어해야함)

#### auth service 구현
- [`Cookie`](#cookie)란?
- [`JWT`](#json-web-token) 기반의 인증 시스템 구현
    - 로그인 성공시 access token과 refresh token 발급
        - 일단 access token은 웹의 스토리지가 아닌 램에서 다룬다
            - 새로고침시 로그인이 유지되어야할 이유가 아직 없다
        - refresh token을 user에게 제공하지 않는 것이 권장된다
            - 서버에서 통제권을 가질 필요가 없는 서비스는 일반적으로 존재하지 않는다고 봐도 과언이 아니다
            - 만료된 access token으로 요청이 들어왔을 때 refresh token이 유효하다면 둘 다 재발급 후 access token을 돌려주게 할 수도 있다
    - spring security의 http security를 통해 토큰 검증 후 인가 정보 관리
    - 해당 토큰은 header fields 중 Authorization을 통해 주고받게 된다
        - `Authorization: Bearer JWT`의 형태로 `Bearer `뒤에 이어붙인다

- 만약 서버가 확장된다면 user service에서 분리되어 api를 통해 접근 가능한 하나의 서비스로 작동해야만 함
    - user service 이외의 서비스가 존재한다면 이미 인증만을 담당하고 각 서비스에서 인가할 수 있게 비대칭 키 형태로 서명하여 공개키를 각 서비스에서 가지고 있을 것이다


## HTTP api with JSON

> 기본적으로 http api는 대부분의 영역을 optional하게 정의해서 이론적으로는 자유롭게 작성 가능하지만 대부분의 기업이 OAuth 2.0을 기반으로 JWT를 사용한 통신을 허용하기때문에 우리가 만드는 서비스도 같은 규격을 사용하도록 하는 것이 좋다


### user, auth service에서의 JWT 발급 및 활용

> 로그인 한 우리 유저인지 아닌지 그때그때 판별하기 위한 도구

- 로그인을 성공한 경우 발급
    - 로그인 시도시 id와 pw를 받아 검증
        - 소셜 로그인의 경우 OAuth 2.0을 기반으로 주어진 정보를 타 서비스에 보내 검증
    - 헤더에서 `Content-Type: application/json`로 지정 후 JSON 형태의 body로 전달
        - 이 때 access token은 당연히 필수적으로 전달해야하지만 refresh token은 서버에서 관리하는 것이 좋다
            - 애초에 stateless라는 속성은 편리함만을 목적으로 한 도구이고 당연히 보안에 좋지 못하다
- 발급 이후 header에서 `Authorization: Bearer JWT`의 형태로 전달하여 요청자의 신원을 보증하는 형태로 쓰인다

- access token과 refresh token은 JWT의 구성요소에서 차이가 있다
    - 공통적인 구성요소
        - header
            - `alg` : 서명 알고리즘
            - `kid` : 서명시 사용한 키의 식별자
        - payload
            - `sub` : 유저의 외부 공개용 고유 식별자 (UUID)
            - `jti` : access token의 고유 식별자 (UUID)
            - `iat` : 발급일시
            - `exp` : 만료일시
    - access token의 추가적인 구성요소
        - payload
            - `role` : 해당 토큰을 발급받은 유저의 권한 정보
    - refresh token만의 추가적인 구성요소는 지금 시점에서는 존재하지 않는다
        - 오히려 JWT의 형태가 꼭 필요한지 고민해봐야한다


#### JWT의 발급과 내부동작

> 애매한 변수의 이름짓기가 가장 힘들다

1. header와 payload의 구성요소를 map 등의 형태로 만든 후 직렬화한다
2. header와 payload를 Base64URL로 인코딩한 header64와 payload64를 만든다
3. header64와 payload64를 '.'을 구분자로 붙인 signing input을 만든다
4. signing input을 서명한 후 Base64URL로 인코딩해 signature를 만든다
5. signing input와 signature를 '.'을 구분자로 붙인 JWT를 완성한다

#### JWT 기반의 RESTful api 기반 등의 통신 예시


- JWT가 없는 유저의 GET요청

```http request (GET)
GET [URL의 PATH] HTTP/1.1
Host: [URL의 HOST(:PORT)]
```

```http response (GET)
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html><html><head>...</head><body>...</body></html>
```

- 로그인을 통한 JWT 발급

```http request (POST)
POST [URL의 PATH] HTTP/1.1
Host: [URL의 HOST(:PORT)]
Content-Type: application/json

{ "key": "value", ... }([Domain][SubAction]RequestDto)
```

```http response (POST)
HTTP/1.1 200 OK
Content-Type: application/json

{ "key": "value", ... }([Domain][SubAction]ResponseDto)
```

- JWT를 가진 유저의 POST

```http request (POST)
POST [URL의 PATH] HTTP/1.1
Host: [URL의 HOST(:PORT)]
Authorization: Bearer [JWT]
Content-Type: application/json

{ "key": "value", ... }([Domain][SubAction]RequestDto)
```

```http response (POST)
HTTP/1.1 200 OK
Content-Type: application/json

{ "key": "value", ... }([Domain][SubAction]ResponseDto)
```

- JWT를 가진 유저의 GET으로 정적 파일을 가져갈 때의 형태

```http request (GET)
GET [URL의 PATH] HTTP/1.1
Host: [URL의 HOST(:PORT)]
Authorization: Bearer [JWT]
```

nginx에서 정적 파일을 반환할 때의 응답 예시

```http response (GET)
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html><html><head>...</head><body>...</body></html>
```

정적 파일이 아니라 api 요청일 때의 응답 예시

```http response (GET)
HTTP/1.1 200 OK
Content-Type: application/json

{ "key": "value", ... }([Domain][SubAction]ResponseDto)
```

### OAuth 2.0

- 예시

```md
Authorization: AuthType Token
Content-Type: application/json

{ "key" : "value", ...}
```

- [OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749)에서 정의되었다

- header fields 중 `Content-Type: application/json`을 통해 body를 json형태로 사용할 수 있다는 부분을 활용했다


- http request의 header fields의 Authorization에서 유저 인증 방식을 다루게 된다
    - JWT는 [Bearer token](https://www.rfc-editor.org/rfc/rfc6750)의 한 종류이다
        - 해당 RFC문서에서 `Authorization: AuthType Token`형태로 정의했다
        - [RFC6749]에서도 JWT이야기가 없는 이유는 단순이 저 시기에 아직 정의되지 않아서이다
            - 그래서 access token이 임의의 난수로 정의되어있다


### RESTful API

- https://[IP_ADDRESS]/domain/{resource-id}/sub-action
    - action은 기본적으로 RFC를 기반으로 한 http method를 사용한다
    - https는 nginx에서 tls 해석 후 http로 reverse proxy 처리하거나 spring security가 직접 처리
        - nginx를 사용할 땐 spring security에서 http를 거부하지 않게 설정해줘야한다 (default로는 허용한다)
        - nginx에서 https를 검증해 http를 넘길 때 `X-Forwarded-*` 헤더를 통해 https기반의 요청임을 spring에게 알릴 수 있고 spring은 인식할 수 있게 설정해줘야 redirect를 `https://`로 생성한다
    - domain은 crud를 할 자원이며 특정하지 않은 조회의 경우 resource-id가 필요하지 않다
        - 복수형으로 작성해야 한다 (domain의 복수형이 어색해서 사용하지 않았다)
    - resource-id는 특정 자원을 식별할 수 있는 식별자로서 기능한다
        - 단순한 정수의 사용은 권장되지 않는다 (방통대 해킹 사태같은 쉬운 접근이 가능해짐)
        - UUID뿐만아니라 문자열 등의 다양한 값을 활용할 수 있다 (당연히 URL에 사용 불가능한 문자는 포함되지 않는다)
        - 상세 페이지처럼 특정하여 조회하는 경우 사용된다
    - sub-action은 특정된 자원을 기반으로 하는 행위를 말한다
        - 해당 domain의 정보 중 일부를 활용하는 경우가 대표적이다

## frontend page?

- login page
- signup page
- profile page
    - profile update page

### SPA / MPA

- SPA가 항상 답인건 아닌데 그렇다고 모든 페이지가 쪼개인 MPA가 쓸만한 서비스인건 아니다
    - index.html, css, router.js등의 기본적인 첫 페이지의 구성요소만 미리 보내두고 페이지 이동시 js파일을 요청해 구성하는 방법도 고려해봤는데 결국 html 리소스를 전송하되 그 내용이 js에 적혀있을 뿐이었다

- css, js library는 서버에 직접 저장하고 전송하게 할 수도, cdn을 통해 가져오게 할 수도 있다

## deployment 

> 기기 내에서 브라우저를 통해 접속하는건 `/etc/hosts`에 사용할 주소가 127.0.0.1을 바라보도록 하면 된다.
> 로컬 네트워크에선 ip가 필요하고 도움 안되는거라 자주 쓰는건 아니다.

### CICD

- CI
    - 별게 없다 깃허브같은 code managing service를 사용해서 source code를 관리하는 상태에서 action을 통해 여러 사람이 지속적으로 협업하여 개발할 수 있으면 된다.
    - github action을 통해 임의의 환경에서 정상적으로 켜지는지 테스트해서 넘기게 하면 편하다. (켜지는지 아닌지와 미리 설정된 테스트를 기반으로 검사하는거지 모든 동작에 오류가 있는지 아닌지를 검사하는 단계가 아니다)


- CD
    - 지속적인 배포는 결국 서버를 완전히 멈추지 않는다는 조건을 만족시켜야한다
        - 그래서 container기반의 docker, docker compose에서도 pod기반의 kubernetes에서도 병렬 구조이기만 하면 가능하다
        - 당연히 하나의 컨테이너만 사용해야만 상황에선 불가능하지만 그럴 일이 없다 
            - 개인 소규모 토이프로젝트에서도 가능한 것이 nginx같은 webserver를 사용해 reverse proxy, health check, server list를 통한 load balancing을 통해 병렬 구조를 만드는 것이기 때문이다
            - 평소에 하나의 컨테이너만 사용하는 구조더라도 새 서버를 새 컨테이너로 빌드해 테스트를 하고 테스트가 끝나면 요청을 새 컨테이너로 보내도록 하여 무중단 상태로 서버를 옮기는 것이 가능하다

---

## frontend knowledge? experience?

### web

#### vanilla javascript

- (html/css/js)
    - SPA를 위한 router 구조 이해

#### library & framework

- vite
- typescript
- react
- nextjs

### app

- android native
    - kotlin

- ios
    - swift

- cross platform
    - flutter


--- 

# 기준점

## status

### 42서울 수료

- inception, 트센 기반의 웹 아키텍처 이해도가 있음

- 42에서 peer-evaluation 준비하듯 내가 할 수 있는 선에서 최대한 상세한 설명을 할 수 있는 기반을 만들어버리는 중...
    - well known standard만 사용할거면 신입을 왜 씀? 검증할 수 있는 사람이 필요한거지

### ??

- flutter로 모바일 앱 제작 실습은 해봄. (api 연동 로그인, 정보 받아오기 정도)

### spring framework experience

- java 기반의 spring 경험 있음
    - CRUD 가능한 mariadb와 연동된 jsp 사이트 제작 경험
    - jdbc, jpa(ORM) 의 단순 사용 경험 있음
- kotlin 기반의 spring boot api 서버 경험 있음
    - 단, 실무적으로 개조되어 스웨거도 있는 세팅 위에서 CRUD api를 추가해 본 경험 수준임
        - .env 직접 세팅
        - swagger를 통해 crud api test해봄

## 실습 기준

- 도메인 영역을 위해 필요한 동작에 대하여 어떤 방식으로 구현할 수 있을지 고민하며 백엔드 서버 구조를 학습한다

- 어떻게 제작할 수 있는지 모르는 상태이기 때문에 먼저 웹 프로젝트 기반으로 백엔드 서버를 만들어보며 이 환경에서 가능한 동작이 무엇인지 배워야한다

- 문서단위 서비스를 기반으로 하기 때문에 nosql의 도입이 필요하지만 user service는 rdbms 기반으로 해야하니 일단 동작을 확인하는 단계인 지금 시점의 실습에서는 mariadb만 사용한다

- 대부분의 서비스는 지금 단계에서 제작하려고 집중할 수 없다. 당장의 목표는 내가 기본적인 백엔드 서버 구성을 할 수 있는 것을 증명할 저수준의 포폴이다.

- TDD 기반으로 의사코드 - 테스트코드 - 개발 순서

- 과정 검증을 위한 지식 정리 이후 컨벤션 및 제약 정의 후 llm을 통한 개발 예정
    - 이 때 최대한 적은 횟수의 지시를 하되 내가 적은 문서의 설계가 잘 전달되는지 (내가 맥락을 부족하게 적은게 없는지) 검증할 예정
- 하네스 엔지니어링 적용을 위한 추가 학습 예정
    - CICD 자동화가 된 상태에서 지속적으로 업데이트 - 즉시배포가 가능한지 확인할 예정
        - 지인분의 llm기반 모바일 대상 웹 게임이 미니게임을 잔뜩 추가중인데 변경점, 추가시 자동으로 업데이트 알림이 나오고 새로고침 유도하는거 보고 관련된 내용을 나도 사용 가능하게 재가공 해볼 예정

---

## Domain

- 옵시디언과 유사한 문서 관리 프로그램
    - 기존 옵시디언의 그래프에 가중치가 없어 완전히 만족스럽지 못했음
    - local 저장소를 기반으로 작동하지만 결국 모든 플랫폼에서 개별적으로 관리해야함
    - 웹을 통해 접근 가능한 로컬 기반으로 저장되는 지식 저장소를 만들고 싶다
    - 내가 원하는 문서만 외부에서 접근 가능하도록 하고 싶다
    - 각 문서에 대한 여러가지 정보가 문서를 외부에 공개하는 시점에서 내가 원하지 않는 정보를 숨길 수 있게 하고 싶다
    - 각 문서의 내용을 합쳐 배치한 새 문서를 만들거나 구성할 수 있어야한다
        - 이 때 각 문서와 통합 문서의 동기화 여부는 아직 결정되지 않았다 (모르겠다)

#### 개요
- markdown 기반의 문서를 해석할 수 있어야한다
- 제텔카스텐 기법을 적용할 수 있어야한다
- 각 문서는 view 모드와 write모드를 가진다
- 문서는 제목, 내용, 메타데이터를 가진다
    - 제목과 내용은 마크다운 형식을 따른다
    - 메타데이터는 view 모드에서 표기되지 않아야한다
    - 내용과 메타데이터는 명백히 구분지어진 UIUX를 가져야한다
    - markdown file로 출력할 수 있어야 한다
        - 메타데이터를 포함할지 여부를 선택할 수 있어야 한다
- 각 문서의 메타데이터에 작성자를 기록할 수 있어야 한다
    - 유저 서비스가 존재해야한다
    - 권한이 어떻게 될지 모르겠지만 최소 해당 문서의 주인만 열람 가능 기능은 있어야한다

#### 주의
- 해당 서비스가 obsidian vault의 정보에 접근해 바로 사용하는지, 읽고 정리하여 db에 저장 후 동작하며 웹에서의 기록을 저장할 때 vault에 문서화 할지, 출력을 요청받지 않는 상황이라면 db에 정보를 저장만 하고 있을지 결정된 부분 없음. 세 가지 동작 이외의 경우도 있을 수 있음


---


## Cookie

> 네트워크 환경에서의 정보 전달 방식과 프론트엔드에서의 저장 방식 및 보안 관련 정보 모음
> 제목은 링크를 위해 간단하게 쿠키라고 했다

### URL

```
[Protocol][Host][:Port][Path][Query][Fragment]

Origin = Protocol + Host + Port
```

- Origin : 세가지 하위영역이 정확히 일치할 때만 같은 오리진이다
    - Protocol : Scheme라고도 표현한다
    - Host
    - Port
- Path : 서버 내부의 실제 directory 구조와 동치가 아니다
    - SPA를 vanilla js 기반으로 라우터를 구성해 구현할 때 history api의 pushState로 관리
    - RESTapi에서 resource를 path의 일부분에 논리적 자원 식별자로 사용한다
    - Next.js의 경우 (dir name)의 형태로 생략되어 실제 구조와 주소의 path가 달라질 수 있다
- Query : ? 이후 &를 구분자로 하여 `name(key)=value`형태로 정보를 전달한다
- Fragment : 서버로 보내지는 것은 아니지만 해당 페이지의 특정 위치를 나타낸다 (RFC 링크 주소에서의 섹션)

### CORS (Cross-Origin Resource Sharing)

- CORS에 해당하는 상황
    - cdn같은 정적 파일 제공 서비스를 사용할 때
        - fetch 등의 http api를 사용하는 경우
        - `type="module"`을 통한 ES Module 로딩의 경우
        - html에서 `<script src>`를 통해 cdn으로 library를 가져오는 경우는 해당하지 않는다
    - MSA 환경(여러 application이 여러 Microservice로 존재)에서 Origin이 일치하지 않는 경우
        - Origin은 일치하지만 Path를 기준으로 서로 다른 서버를 사용하는 경우는 해당하지 않는다

### 쿠키와 세션, 로컬스토리지

> 당연한거지만 RAM이 아닌 영구저장 가능한 영역을 기반으로 고민해봐야한다
> 사용자의 요청에 따라 제공된 사용자의 권한상 인가된 모든 정보를 물리적으로 저장해버리면 바로 보안 취약점이 될 듯
> 이것도 RFC로 정의된 영역이긴 한데 한 문서를 다 쓰지 않아서 담지 않기로 함

- http cookie
    - [RFC 6265](https://www.rfc-editor.org/info/rfc6265)
    - http와 다르게 브라우저와의 통신에서만 활용 가능한 특수한 형태의 저장소이며 통신 규격
        - 웹/앱을 전부 포괄하는 api를 만들 때에도 cookie container가 제공되는 경우 다룰 수는 있지만 권장되지 않는 방법이다
            - 쿠키 속성까지 동일하게 다루지 않는다고 한다 
        - 쿠키 발급도 세션, JWT처럼 서버에서 진행한다
            - 클라이언트가 프론트에서 다룰 수 있기때문에 보안상 최대한 막아야한다
    - default는 client에서 javascript로 마음대로 다룰 수 있기때문에 주의해야한다
    - session, JWT등의 다른 것과 마찬가지로 최초 접속시엔 쿠키가 없고 재 로그인을 해야할 때는 필요가 없다
    - server에서 http api의 header에 `Set-Cookie`필드를 통해 클라이언트측 브라우저에 요청
        - CORS등의 Origin(Protocol + Host + Port)이 달라지는 상황에선 추가 설정이 필요하다
            - 프론트엔드 측에서 credentials 옵션을 true로 설정해줘야한다
                - fetchAPI : `credentials: 'include'`
                - Axios : `withCredentials: true`
            - 백엔드 측에서 정책 설정이 되어있어야 한다
                ```
                Access-Control-Allow-Origin: http://localhost:3000
                Access-Control-Allow-Credentials: true
                Access-Control-Allow-Methods: GET, POST, PUT, DELETE
                Access-Control-Allow-Headers: Content-Type, Authorization
                ```
        - header fields의 Set-Cookie의 값은 ';'을 구분자로 키-값 쌍을 나누고 각 쌍에선 '='을 구분자로 key와 value를 나눈다
            - 이 때 첫번째 위치의 키-값쌍이 실제 쿠키이고 그 이후엔 해당 쿠키의 제어 속성이 온다
                - `Cookie prefix` : 실제 쿠키의 이름 앞에 접두로 `__Host-`를 붙여 Secure, Path를 필수로 만들고 서브도메인이 절대 덮어쓸 수 없는 단일 호스트 전용임을 명시할 수 있음
            - 키=값 쌍 형태의 속성
                - `Domain=<도메인>` : 쿠키가 전송될 도메인 범위 제한 (생략시 current Host) (화이트리스트)
                - `Path=<경로>` : 쿠키가 전송될 URL Path 범위 제한 (화이트리스트)
                    - 쿠키의 전송 범위를 재발급 엔드포인트로 한정하여 다른 api요청에서 사용되지 않게 할 수 있음
                - `Max-Age=<초 단위의 정수>` : 쿠키의 유효 수명 (만료시 자동 삭제)
                - `Expires=<DD Mon YYYY HH:MM:SS GMT>` : 만료일시 (Max-Age가 선순위)
                    - Max-Age나 Expires 속성이 모두 존재하지 않을 땐 RAM에만 저장한다
                - `SameSite=<Strict|Lax|None>` : 자동 전송 차단 범위 (CSRF 방어)
                    - `Strict`(엄격) : 다른 도메인에서 들어오는 모든 요청에서 쿠키 차단
                        - 들어와서 새로고침해야 쿠키 전달 가능
                    - `Lax`(기본) : 다른 도메인의 요청 중 GET을 통해 브라우저 주소창이 Domain과 일치하는 경우 허용 
                    - `None`(완전 허용) : 모든 요청에서 쿠키를 보내줌 (Secure 속성 필수)
            - 단독 플래그 형태의 속성
                - `HttpOnly` : js에서의 document.cookie 접근 차단 (XSS 토큰 탈취 방어)
                    - js에서 만든 쿠키에서는 설정 할 수 없음
                - `Secure` : HTTPS(TLS) 연결에서만 전송하도록 강제 (스니핑 방어)
    - 보안 위협의 종류
        - XSS (Cross-Site Scripting) : JS의 document.cookie를 통한 탈취
        - CSRF (Cross-Site Request Forgery) : 탈취할 사이트인 척 내 서버에 전송을 보냈을 때 보안 설정이 안되어있다면 자동적으로 쿠키를 보내주는 기능 악용
        - 스니핑 (Packet Sniffing) : 공용 네트워크 등의 암호화되지 않은 HTTP 패킷을 가로채 평문으로 된 정보를 탈취하는 위협
        - XSS을 통한 API 대리 호출 (Session Riding) : refresh token이 쿠키에 저장된 경우 스크립트가 직접 읽지는 못해도 브라우저를 시켜 재발급 API를 쏘면 새로운 Access Token이 탈취됨


- session
    - 기본적으로는 서버에서 ram에 저장소를 만들어 두는 방식
        - session을 만들 때 session id를 발급해 클라이언트에게 전달한다
            - 이 때 쿠키, URL 파라미터, Authorization 등의 다양한 방식이 가능하다
            - session id는 직접 만들어도 되지만 무작위의 UUIDv4를 사용해도 좋다
        - 서버에 문제가 생기면 휘발된다
        - 스레드 단위에서 제한적으로 공유할 방법은 있어도 프로세스나 컨테이너 단위에선 공유할 수 없다
    - 별도의 외부 저장소를 통해 관리할 수 있다
        - 파일 기반으로 외부 저장소를 만들 수 있다
            - IPC를 통해 프로세스 단위의 공유가 가능하다
            - 같은 Host 위의 container까지는 volume을 통해 공유할 수 있다
        - Redis나 dbms를 통해 다른 Host의 container에서도 공유할 수 있게 할 수 있다
    - 클라이언트는 세션 키를 기반으로 통신한다
        - jwt를 사용할때와 같은 방식이다

- web storage
    - 브라우저가 관리하는 Origin 단위의 저장공간
        - 일반적으로 사용자의 기기에 파일 단위로 영구저장하는 방식은 다운로드를 통해 진행된다
    - javascript를 통해 접근 및 제어 가능하다 (막을 수 없다)
    - 웹 스토리지는 두가지 영역으로 뉜다
        - localStorage : Origin 당 약 5MB정도의 영구 저장소
        - sessionStorage : 창이나 탭 영역에서 살아있을 때 유지되는 저장소

- app storage
    - 앱은 앱마다 주어지는 전용 격리 공간을 사용하거나 앱 권한을 받아 로컬 스토리지에 접근하는 두가지 방법이 있다.
        - Internal Storage (앱의 전용 격리 폴더) : SharedPreferences, UserDefaults, SQLite DB
    - 앱의 저장공간이나 로컬 스토리지는 손쉽게 탈취 가능하다
        - 인증, 인가에서 사용할 JWT같은 데이터는 각 os의 하드웨어 암호화 저장소에 저장해야한다
            - Android : keystore
            - iOS : keychain

- 최종적으로 알아야 할 보안 전략
    - DPoP (Proof-of-Possession, RFC 9449) : 클라이언트가 비대칭 개인키로 매 요청마다 서명을 생성하여, 토큰 문자열이 탈취되어도 해커가 단독으로 사용할 수 없게 만듦
    - RTR (Refresh Token Rotation) : access token 재발급시 refresh token도 재발급
        - 재사용 감지 시 해당 유저의 모든 세션 강제 폭파
            - 단순히 요청이 중복된 경우를 위해 각 요청이 멱등성 key를 가질 수 있게 해야한다
    - MTLS (Mutual TLS, RFC 8705) : 토큰을 클라이언트의 TLS 인증서에 바인딩하여 네트워크 연결 계층에서 위조 차단

---

# UUID

## UUIDs

- 범용 고유 식별자
    - 16byte(128bit)의 정수
    - 4-2-2-2-6의 형태로 표기한다
        - hexadecimal string으로는 8-4-4-4-12의 형태
    - 일반적인 네트워크 프로토콜을 통해 전송될 값 답게 빅 엔디안을 사용한다
        - 단, 마이크로소프트의 COM GUID는 부분적으로 리틀 엔디안을 사용한다고 한다

- hexadecimal로 입력받을 때 대소문자를 구분하지 않아야 한다
    - 정작 생성시 SHOULD use lower case 이다

- UUID 자체의 정보인 변형, 버전 필드는 시작 위치와 값이 정해져 있다
    - 단, Nil UUID(0), Max UUID(1)의 두 경우는 예외이다
    - 구분자 '-'으로 나눠진 5개의 영역 중 3, 4번째 영역의 왼쪽에서 시작한다
        - Variant Field : 4번째 영역의 첫 hexadecimal
            - 0 ~ 7 [0xxx] : NCS 하위 호환성을 위한 변형 필드 (Nil UUID 포함)
            - 8 ~ b [10xx] : RFC 9562에서 정의하는 표준 UUID 변형 필드
            - c ~ d [110x] : MS의 변형 필드
            - e ~ f [111x] : 향후 정의를 위해 예약된 영역 (Max UUID 포함)
        - Version Field : 3번째 영역의 첫 hexadecimal
            - 각 variant마다 다른 방식을 사용한다
            - Variant Field가 8 ~ b [10xx]일 때
                - 0     : Unused
                - 1 ~ 8 : 각 버전
                - 9 ~ f : 향후 정의를 위해 예약된 영역

## UUID Layouts

> 버전만 잘 선택하면 다 알아서 만들어주는 라이브러리가 있다
> 근데 어떤 버전을 사용할지에 대한 트레이드오프 고민하려면 일단 알긴 해야함

- 내부 구성이 궁금하면 이쪽으로 -> [아르곤 시켜서 정리된 버전](#uuid_argon)
    - 직접 서식 만들고 RFC의 표까지 만들었는데 1, 2버전 정리해보니 어차피 안 다룰 상세 내용들이라 제미나이 아르곤에게 원문과 내 서식 둘 다 줘서 정리시킴

## UUID versions

> 중요한 것만 빠르게 정리하자

- 완전 난수 : v4
- timestamp 기반 : v1 -> v6 -> v7
- namespace hash 기반 : v3 (MD5) -> v5 (SHA-1)
- DCE Security : v2
- custom : v8

- 여기서 v4, v7 중 하나를 사용하는 것이 일반적이며 정렬이 필요하다면 v7을 사용 가능하지만 누구나 일시를 확인 가능하다는 단점이 있다
    - 물론 다른 버전을 쓰지 말라는게 아니다


## UUID Reference

- [UUIDs - RFC9562](https://www.rfc-editor.org/info/rfc9562)

- UUID의 format은 ABNF를 따른다
    - [ABNF - RFC5234](https://www.rfc-editor.org/info/rfc5234)
    ```
    UUID     = 4hexOctet "-"
           2hexOctet "-"
           2hexOctet "-"
           2hexOctet "-"
           6hexOctet
    hexOctet = HEXDIG HEXDIG
    DIGIT    = %x30-39
    HEXDIG   = DIGIT / "A" / "B" / "C" / "D" / "E" / "F"
    ```

- [IANA UUID Subtype Registry and Registration](https://www.rfc-editor.org/info/rfc9562/#section-7.1)

|Name | ID | Subtype | Variant | Reference|
|---|---|---|---|---|
|Gregorian Time-based|1|version|OSF DCE / IETF|[RFC4122], [RFC9562]|
|DCE Security|2|version|OSF DCE / IETF|[C309], [C311]|
|MD5 Name-based|3|version|OSF DCE / IETF|[RFC4122], [RFC9562]|
|Random|4|version|OSF DCE / IETF|[RFC4122], [RFC9562]|
|SHA-1 Name-based|5|version|OSF DCE / IETF|[RFC4122], [RFC9562]|
|Reordered Gregorian Time-based|6|version|OSF DCE / IETF|[RFC9562]|
|Unix Time-based|7|version|OSF DCE / IETF|[RFC9562]|
|Custom|8|version|OSF DCE / IETF|[RFC9562]|

---

# HTTP

## HyperText Transfer Protocol

- [HTTP Documentation](https://httpwg.org/specs/)

- HTTP/0.9 (1991)
- HTTP/1.0 (1996)
- HTTP/1.1 (1997)
    - 여기까진 사람이 헤더를 직접 읽을 수 있다
    - [중단된 구버전 - RFC 2616](https://www.rfc-editor.org/rfc/rfc2616)
    - [최신 버전 - RFC 9112](https://www.rfc-editor.org/rfc/rfc9112)
- HTTP/2.0 (2015)
    - 헤더가 이진화되어 더 빠르고 효율적으로 변경됨
    - 표준에서는 TLS가 강제되지 않지만 모든 브라우저는 TLSv1.2이상을 필수적으로 요구하여 표준과 달리 사실상 필수적인 구성요소가 되었다
    - HTTP/2.0 표준이 아니라 브라우저에서 요구하는 것을 기준으로 개발해야만 한다
- HTTP/3 (2022)
    - QUIC를 사용하기 위해 UDP를 기반으로 한다
        - TCP는 더이상 사용되지 않는다
    - TLSv1.3을 기본적으로 요구한다

```request
[METHOD] [PATH] [Protocol version]
[headers]

[body]
```

```response
[Protocol version] [STATUS CODE] [STATUS MESSAGE]
[headers]

[body]
```

```request headers
GET / HTTP/1.1
Host: developer.mozilla.org
Accept-Language: ko
```

```response headers
HTTP/1.1 200 OK
Date: Sat, 09 Oct 2010 14:28:02 GMT
Server: Apache
Last-Modified: Tue, 01 Dec 2009 20:18:22 GMT
ETag: "51142bc1-7449-479b075b2891b"
Accept-Ranges: bytes
Content-Length: 29769
Content-Type: text/html

<!DOCTYPE html... (here comes the 29769 bytes of the requested web page)
```

- 정말 자세히 알고싶다면 webserv를 검색해서 많은 정보를 알아낼 수 있다
- HTTP/1.1 버전의 nginx의 config와 유사한 컨피그 파일을 읽어 동작해야하는 웹 서버를 만들어보는 ecole42 5서클의 프로젝트이다

- [http method - RFC 9110](https://www.rfc-editor.org/info/rfc9110/#section-9)
- [IANA](https://www.iana.org/assignments/http-methods)

- method는 다양하게 있지만 서버에서 MUST로 지원해야하는 것은 GET과 HEAD뿐이고 나머지는 optional하다
    - 특정 서비스 영역에선 보안 문제로 다수의 서비스가 POST 요청만 통과시킨다고 한다

- RESTful api를 통해 GET POST PUT DELETE까지는 자주 사용된다
    - 물론 GET POST 외의 다른건 실무적으로 복잡한 케이스를 포함하지 못해 자주 사용되지는 않는다고 한다
    - 심지어 GET은 body가 일반적이지 않아 (Undefined behaviour) 모든 경우에서 허용된 사용이 보장된 메서드도 아니고 Path의 길이 제한도 있어 요청할 때도 data를 전송해야하는경우 사용이 불가하다고 한다

- 멱등성을 보장하는 method는 GET, HEAD, PUT, DELETE, OPTIONS 등이 있다
    - POST 자체로는 멱등성이 보장되지 않기 때문에 멱등성 키를 따로 사용해 보장하기 위한 노력을 해야한다

- [status code](https://developer.mozilla.org/ko/docs/Web/HTTP/Reference/Status) 3자리 정수로 구성된다
    - [RFC 2616 -10](https://www.rfc-editor.org/info/rfc2616/#section-10)
    - 분류
        - 1xx : informational responses
        - 2xx : success
        - 3xx : redirection
        - 4xx : client errors
        - 5xx : server errors
    - 상세한 코드가 존재하지만 사용자의 UI에서는 00으로 통일하여 불필요하게 자세한 정보를 제공하는것은 피해야한다
    - client는 몰라야하지만 frontend에서 필요한 status code는 전달되어야한다
        - 401, 403, 404등의 frontend에서 backend에게 추가적인 작업을 요청하거나 해당 상태에 따라 다르게 동작해야하는 경우가 있다
        - 보안을 위해 client의 error UI에선 한가지로만 표기되어야만한다

- [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110)
    - method, status code, fields를 포함하는 HTTP message에 대한 최신 표준이다
    - 그렇다 http header는 이제 없다 fields로 대체되었다
        - [HTTP headers](#http-headers) 열심히 정리했는데....?

## HTTP fields

- `Headers` 대신 `Fields`(`Header Fields` + `Trailer Fields`)로 변경되었다
    - [Message Abstraction - RFC 9110](https://datatracker.ietf.org/doc/html/rfc9110#section-6)
    - chunked 전송 등에서 본문 맨 뒤에 붙는 `Trailer`도 `Key: Value` 형태를 쓰고 위치상 당연히 header가 아니기 때문에 두 영역을 포괄하는 표현으로 변경되었다
        - trailer field의 대표적인 요소로 here_doc의 EOF같은 역할도 하는 Content-Digest가 있다
            - 이때 header field에 `Trailer: Content-Digest`를 명시해둬야한다
            - trailer field의 Content-Digest의 value로는 체크섬을 위한 값이 사용할 수 있다
            - Content-Digest는 Content-MD5를 대체했다 (RFC 9530에서 대체됨)
    - HTTP/1.1과 달리 HTTP/2, HTTP/3부터는 텍스트 기반의 Header Line이 아니라 이진 프레임 내부의 data field 형태로 압축 전송되어 fields가 더 적합한 표현이 되었다

### Header fields, Trailer fields

- [RFC 9110](https://datatracker.ietf.org/doc/html/rfc9110)
    - 과거 RFC 2616의 4가지 분류 대신 역할(컨텍스트)에 따라 분류한다
    - 하나의 섹션에 정리되어있지 않고 다양한 섹션에 걸쳐 그 상황에서 필요한 헤더의 예시를 표현하는 방식으로 서술되어 있다


### fields의 유효 거리

- hop by hop
    - next proxy까지만 유효한 fields
    - proxy에게 특정한 동작을 요구한다
    - [RFC 9110](https://datatracker.ietf.org/doc/html/rfc9110#section-7.6.1)에 정의된 목록
        1. Connection
        2. Keep-Alive
        3. Proxy-Authenticate
        4. Proxy-Authorization
        5. Trailer
        6. TE
        7. Transfer-Encoding (예: chunked)
        8. Upgrade (웹소켓 전환용)
            - nginx에선 웹소켓을 허용하기 위해 두 줄을 명시해줘야한다
                - `proxy_set_header Upgrade "$http_upgrade"`
                - `proxy_set_header Connection "upgrade"`

- end to end
    - 처음부터 끝까지 유효한 fields
    - hop by hop이 아닌 모든 fields가 해당됨

---

# expired.....

## HTTP headers

- [HTTP headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers)

- 진짜 알고 적어야하는 헤더가 뭔지 알아내서 정리를 해야 할 것 같다
    - [RFC 4229](https://datatracker.ietf.org/doc/html/rfc4229)에만 130개 넘게 정의되어 있다

- [RFC 2616](https://www.rfc-editor.org/rfc/rfc2616)을 기준으로 4가지 영역의 header가 정리되어 있다
    1. General Header (RFC2616#4.5)
        - request와 response에 공통적으로 사용되는 header
        - 전송되는 entity에는 적용되지 않는 헤더 필드가 있다
    2. Request Header (RFC2616#5.3)
        - request에서만 사용되는 header
    3. Response Header (RFC2616#6.2)
        - response에서만 사용되는 header
    4. Entity Header (RFC2616#7.1)
        - message body를 가지는 request와 response 모두 사용되는 header

### headers의 유효 거리

- hop by hop
    - next proxy까지만 유효한 header
    - proxy에게 특정한 동작을 요구한다
    - [RFC 2616](https://datatracker.ietf.org/doc/html/rfc2616#section-13.5.1)에 정의된 목록
        1. Connection
        2. Keep-Alive
        3. Proxy-Authenticate
        4. Proxy-Authorization
        5. Trailer
        6. TE
        7. Transfer-Encoding (예: chunked)
        8. Upgrade (웹소켓 전환용)
            - nginx에선 웹소켓을 허용하기 위해 두 줄을 명시해줘야한다
                - `proxy_set_header Upgrade "$http_upgrade"`
                - `proxy_set_header Connection "upgrade"`

- end to end
    - 처음부터 끝까지 유효한 header
    - hop by hop header가 아닌 모든 헤더가 해당됨

---

# certification

- CA(Certificate Authority)
    - self-signed certificate는 신뢰할 수 없는 대상 중 하나이다 (openssl로 대충 만든거니...)


- CA-certificate
    - TLS Handshake 과정에서 신뢰할 수 있는 최상위 인증 기관들의 Root CA public key의 목록을 제공해주는 데이터 패키지
    - package manager를 통해 cli환경에서의 명령어(프로그램 등의 패키지)을 설치한다면 항상 보이고 주기적으로 업데이트된다

- openssl
    - 단순히 암복호화 연산을 해주는 c 프로그램
    - ssh에서 ssh-keygen이나 암호화, 복호화는 여기에 맡겼다
    - 범용 암호화 라이브러리인 libcrypto, libssl를 기반으로 만들어졌다
        - 최신 OpenSSH는 LibreSSL의 자체 내장 암호화 코드를 쓰거나 OpenSSL의 libcrypto를 링크해서 사용한다

- letsencrypt
    - 무료 공인 인증 기관
    - 단 90일마다 만료되어 인증을 계속하려면 주기적으로 갱신을 해야만 한다
    - certbot
        - nginx등의 웹 서버의 config를 참조해 자동으로 인증서를 갱신해주는 프로그램
        - 만료 30일 전마다 연장해준다

---

> 세부 주소 경로의 시작점을 `rfc`대신 `info`로 교체 후 `.html`을 지우면 더 보기 좋은 사이트가 나온다

# TLS

## SSL / TLS

- SSL(Secure Sockets Layer)은 1.0, 2.0, 3.0이 있는데 전부 금지되었다
    - SSL 1.0은 치명적인 보안 결함으로 인해 공개된 적도 없다
    - [SSL 2.0 금지 - RFC 6176](https://www.rfc-editor.org/rfc/rfc6176.html)
    - [SSL 3.0 금지 - RFC 7568](https://www.rfc-editor.org/rfc/rfc7568.html)

- TLS (Transport Layer Security)
    - AES 기반의 대칭키를 통해 더 효율적으로 통신을 암호화한다
    - [TLS 1.0 - RFC 2246](https://www.rfc-editor.org/rfc/rfc2246.html)
    - [TLS 1.1 - RFC 4346](https://www.rfc-editor.org/rfc/rfc4346.html)
    - [TLS 1.2 - RFC 5246](https://www.rfc-editor.org/rfc/rfc5246.html)
    - [TLS 1.3 - RFC 8446](https://www.rfc-editor.org/rfc/rfc8446.html)

- 인증서를 필수적으로 요구하며 self-signed certificate를 통해 개발하는 경우 브라우저에서 경고 무시를 해야한다

## deprecating TLS 1.0 and TLS 1.1

- [TLS 1.0, 1.1 지원 중지 권고 - RFC 8996](https://www.rfc-editor.org/info/rfc8996/)

---

# OAuth (Open Authorization)

- [OAuth 1.0 - RFC 5849](https://www.rfc-editor.org/rfc/rfc5849.html)
- [OAuth 2.0 - RFC 6749](https://www.rfc-editor.org/rfc/rfc6749.html)
    - [OAuth2.0 for Native Apps - RFC 8252](https://www.rfc-editor.org/rfc/rfc8252.html)
- [OAuth 2.0 : Bearer Token Usage - RFC 6750](https://www.rfc-editor.org/rfc/rfc6750.html)
- [OAuth 2.1](유예중)

[OAuth 공식 홈페이지](https://oauth.net/2/)

- 보안 문제로 1.0, 1.0a는 사용하지 않는다
- OAuth 2.0은 많은 수정이 이루어져있고 현재 OAuth 2.1이 새 표준으로 만들어지고 있는 상태이다
- OAuth 2.1은 당분간 표준이 될 수 없어보이니 OAuth 2.0을 기반으로 하더라도 2.1에서 추가되는 중요한 내용은 미리 적용할 수 있어야 한다
    - 소셜 로그인이 가능한 회사들 대부분이 이미 2.1의 내용을 지켜야만하게 제약한다

---

# JSON Web Token

## JWT의 종류
- `JWT`는 `JWS (JSON Web Signature)`와 `JWE (JSON Web Encryption)`로 나뉠 수 있다.
    - 기본적으로 우리가 api를 만들 때 사용하는 형태가 `JWS`이다
    - `JWE`는 Base64URL 인코딩만 되어있는 `JWS`와 달리 메세지 전체가 암호화(encryption)되어있다
    - 어떤 값도 넣을 수 있기때문에 중첩 토큰(`Nested JWT`)이 가능하며 엄밀하게 따지자면 JWT는 명확하게 두 영역으로 나뉘지 않는다
- JWS에서는 header, payload, signature로 JWE에서는 header, encrypted_key, iv, ciphertext, tag로 구성되며 JWS에서의 header의 alg, JWE에서의 header의 alg, enc만이 필수(MUST)이고 이 외의 모든 claim은 optional하다
- http api에서 request에서 header fields의 영역에서 `Authorization: Bearer [JWT]` 와 같은 형태로 전달된다

```javascript
// JWE
BASE64URL(JWE Protected Header) || '.' ||
BASE64URL(JWE Encrypted Key) || '.' ||
BASE64URL(JWE Initialization Vector) || '.' ||
BASE64URL(JWE Ciphertext) || '.' ||
BASE64URL(JWE Authentication Tag)

// JWS
BASE64URL(JWS Protected Header) || '.' ||
BASE64URL(JWS Payload) || '.' ||
BASE64URL(JWS Signature)
```

## JWT 관련 RFC 문서와 간단한 설명

> irc처럼 RFC문서를 기반으로 학습하려고 알아본건데 그냥 문서 정리만 해두고 개념은 다른데서 구해서 정리하도록 하자

- [JWS - RFC 7515](https://www.rfc-editor.org/rfc/rfc7515.html) : `header`에서 암호화 관련 요소
- [JWE - RFC 7516](https://www.rfc-editor.org/rfc/rfc7516.html) : 토큰 전체 `encryption`한 특수 규격
- [JWK - RFC 7517](https://www.rfc-editor.org/rfc/rfc7517.html) : JWT를 통해 key를 주고받을 때의 규격
- [JWA - RFC 7518](https://www.rfc-editor.org/rfc/rfc7518.html) : `JWT signature` 암호화 알고리즘
- [JWT - RFC 7519](https://www.rfc-editor.org/rfc/rfc7519.html) : JWT 정의 문서
- [JWT (updated) - RFC 7797](https://www.rfc-editor.org/rfc/rfc7797.html) : payload에서 Base64URL 안쓰기 (...? 왜?)
- [JWT (updated) - RFC 8725](https://www.rfc-editor.org/rfc/rfc8725.html) : 보안 체크리스트
- [JWT for OAuth 2.0 - RFC 9068](https://www.rfc-editor.org/rfc/rfc9068.html) : OAuth 2.0에서의 JWT 권장 규격
- [JWA (updated) - RFC 9864](https://www.rfc-editor.org/rfc/rfc9864.html) : JWT signature 암호화 알고리즘의 업데이트 버전 문서
- 이 외에도 있고, 추가될 수 있지만 이정도만 정리해두면 될 것 같다

## JWT(JWS)

- header
    - 해당 토큰에 대한 정보
    - JWS, JWE의 header 구성이 다르고 경우에 따라 선택해 구성해야한다
    - 기본적으로 `alg`라는 서명 알고리즘을 필수로 가져야하며 JWE의 경우 `enc`도 필수로 가져야한다
- payload
    - 이 영역에선 registered claim과 겹치지 않는 모든 것이 허용된다
    - public claim으로 등록된 영역은 관련된 서비스(OAuth 등)를 사용하는 이상 피해야한다
    - 우리가 만들어 쓰는 claim은 private claim에 속한다고 할 수 있다
- signature
    - header와 payload를 Base64URL 인코딩 후 구분자 '.'으로 연결한 뒤 secret key로 sign한 값
    - Sign할 때 쓴 key는 서버에만 존재하므로 같은 결과가 나왔는지 확인해 정상적으로 발급된 토큰인지 확인한다
        - 인증, 인가 서버가 동일한 환경에서 대칭키로 HS256 이상을 사용해야한다 (4byte같은거 쓰다 털린 서버도 있다고 한다...)
        - 단, 인증(발급)과 인가(검증) 서버가 분리된 환경의 경우 대칭키가 아닌 RS256, ES256 등의 비대칭키를 사용하여 인증(발급) 서버에서 private key, 인가(검증) 서버에서 public key를 가져야한다
- 세 영역은 '.'을 구분자로 사용한다
    - Base64URL(header).Base64URL(payload).Base64URL(signature(Base64URL(header).Base64URL(payload), key))
- 암호화되어있지 않음
    - 열람은 모두 가능
    - 시그니처의 의의는 내가 생성한 JWT가 맞는지 확인하는 것이다
- ascii는 Base128, 확장 아스키는 Base256이라고도 할 수 있겠다
- Base64 `AZaz09+/` (`=` 4글자 규칙을 위한 빈칸 padding용 문자 url에서는 사용되지 않는다)
    - url에서 구분자로 사용하는 /, = 및 공백으로 해석되는 +를 사용하고있다
- Base64URL `AZaz09-_`
    - url에서 구분자로 사용하지 않는 '+'를 대체하는 '-', '/'를 대체하는 '_'를 사용하며 패딩은 사용하지 않는다

- `NumericDate`
    - JWT - RFC7519 2. Terminology - NumericDate에서 확인 가능
    - 1970-01-01T00:00:00Z UTC를 기준으로 초 단위 표기
    - 윤초 없이 모든 1d는 86400s로 계산한다
        - 1d = 24(h) * 60(m) * 60(s)
        - 현재 시간을 기준으로 하여 초 단위로 변환한 값을 더하거나 빼서 사용한다
    - payload의 exp, nbf, iat에서 사용된다


```json (header)
{
    "typ": "JWT", # JWS라고 안쓰고 JWT라고 쓴다
    "alg": "signature algorithm", # signature를 생성할 때 쓴 algorithm
    "kid": "key id", # signature를 생성할 때 쓴 key의 id(name)
}
```

```json (payload)
{
# Registered Claims
    # String
    "iss": "issuer", # 토큰 발급자
    "sub": "subject", # 토큰 사용자
    "aud": "audience", # 토큰 수신자
    "jti": "jwt id", # 토큰 고유 식별자
    # NumericDate
    "exp": "expiration date", # 만료 일시
    "nbf": "not before date", # 활성화 시작 일시
    "iat": "issued at date", # 발급 일시
# Public Claims (IANA 공식 등록 또는 충돌 방지 URI)
    # [OIDC / OAuth 2.0 표준 공용 클레임]
    "email": "user@example.com",       # 사용자 이메일 (OIDC 표준)
    "email_verified": true,            # 이메일 인증 완료 여부 (OIDC 표준)
    "name": "Hong Gil-Dong",           # 사용자 전체 이름 (OIDC 표준)
    "picture": "https://.../img.jpg",  # 프로필 이미지 URL (OIDC 표준)
    "locale": "ko-KR",                 # 사용자 언어/지역 (OIDC 표준)
    "scope": "read write profile",     # OAuth 2.0 권한 범위 (RFC 9068)
    "client_id": "my-client-app-1",    # OAuth 2.0 클라이언트 ID (RFC 9068)
    # [충돌 방지 URI 형태의 공개 클레임]
    "https://example.com/jwt/role": "admin"  # 도메인 네임스페이스를 활용한 충돌 방지 키
# Private Claims
}
```

- 기본적인 토큰 생성 과정 이해를 위한 js에서 JWT를 만드는 의사코드
    - Base64URL나 Sign은 실존하지 않는다(물론 할수도 있다)
    - 다만 대부분의 개발환경에서 적합한 라이브러리가 존재할것이다

```js tokenizer의 의사코드
jwt_header = {...};
jwt_payload = {...};

jwt_encode_header = Base64URL.encode(JSON.stringify(jwt_header));
jwt_encode_payload = Base64URL.encode(JSON.stringify(jwt_payload));

jwt_signature = Sign(jwt_encode_header + '.' + jwt_encode_payload, key);
jwt_encode_signature = Base64URL.encode(jwt_signature);

jwt_token = `${jwt_encode_header}.${jwt_encode_payload}.${jwt_encode_signature}`;
```


## JWT header parameter, payload claim 정리

> 쓸 일이 있을까싶지만 RFC문서에서 header의 parameter와 payload의 claim을 정리해둠

```markdown (header - JWS)
- Header Parameter Name: "alg"
- Header Parameter Description: Algorithm
- Header Parameter Usage Location(s): JWS
- Change Controller: IESG
- Specification Document(s): Section 4.1.1 of RFC 7515

- Header Parameter Name: "jku"
- Header Parameter Description: JWK Set URL
- Header Parameter Usage Location(s): JWS
- Change Controller: IESG
- Specification Document(s): Section 4.1.2 of RFC 7515

- Header Parameter Name: "jwk"
- Header Parameter Description: JSON Web Key
- Header Parameter Usage Location(s): JWS
- Change Controller: IESG
- Specification Document(s): Section 4.1.3 of RFC 7515

- Header Parameter Name: "kid"
- Header Parameter Description: Key ID
- Header Parameter Usage Location(s): JWS
- Change Controller: IESG
- Specification Document(s): Section 4.1.4 of RFC 7515

- Header Parameter Name: "x5u"
- Header Parameter Description: X.509 URL
- Header Parameter Usage Location(s): JWS
- Change Controller: IESG
- Specification Document(s): Section 4.1.5 of RFC 7515

- Header Parameter Name: "x5c"
- Header Parameter Description: X.509 Certificate Chain
- Header Parameter Usage Location(s): JWS
- Change Controller: IESG
- Specification Document(s): Section 4.1.6 of RFC 7515

- Header Parameter Name: "x5t"
- Header Parameter Description: X.509 Certificate SHA-1 Thumbprint
- Header Parameter Usage Location(s): JWS
- Change Controller: IESG
- Specification Document(s): Section 4.1.7 of RFC 7515

- Header Parameter Name: "x5t#S256"
- Header Parameter Description: X.509 Certificate SHA-256 Thumbprint
- Header Parameter Usage Location(s): JWS
- Change Controller: IESG
- Specification Document(s): Section 4.1.8 of RFC 7515

- Header Parameter Name: "typ"
- Header Parameter Description: Type
- Header Parameter Usage Location(s): JWS
- Change Controller: IESG
- Specification Document(s): Section 4.1.9 of RFC 7515

- Header Parameter Name: "cty"
- Header Parameter Description: Content Type
- Header Parameter Usage Location(s): JWS
- Change Controller: IESG
- Specification Document(s): Section 4.1.10 of RFC 7515

- Header Parameter Name: "crit"
- Header Parameter Description: Critical
- Header Parameter Usage Location(s): JWS
- Change Controller: IESG
- Specification Document(s): Section 4.1.11 of RFC 7515
```

```markdown (header - JWE에서 추가된 header parameter)
- Header Parameter Name: "enc"
- Header Parameter Description: Encryption Algorithm
- Header Parameter Usage Location(s): JWE
- Change Controller: IESG
- Specification Document(s): Section 4.1.2 of RFC 7516

- Header Parameter Name: "zip"
- Header Parameter Description: Compression Algorithm
- Header Parameter Usage Location(s): JWE
- Change Controller: IESG
- Specification Document(s): Section 4.1.3 of RFC 7516
```

```markdown (header - JWE에서 추가할 수 있는 payload의 claim)
- Header Parameter Name: "iss"
- Header Parameter Description: Issuer
- Header Parameter Usage Location(s): JWE
- Change Controller: IESG
- Specification Document(s): Section 4.1.1 of RFC 7519

- Header Parameter Name: "sub"
- Header Parameter Description: Subject
- Header Parameter Usage Location(s): JWE
- Change Controller: IESG
- Specification Document(s): Section 4.1.2 of RFC 7519

- Header Parameter Name: "aud"
- Header Parameter Description: Audience
- Header Parameter Usage Location(s): JWE
- Change Controller: IESG
- Specification Document(s): Section 4.1.3 of RFC 7519
```

```markdown (payload)
- Claim Name: "iss"
- Claim Description: Issuer
- Change Controller: IESG
- Specification Document(s): Section 4.1.1 of RFC 7519

- Claim Name: "sub"
- Claim Description: Subject
- Change Controller: IESG
- Specification Document(s): Section 4.1.2 of RFC 7519

- Claim Name: "aud"
- Claim Description: Audience
- Change Controller: IESG
- Specification Document(s): Section 4.1.3 of RFC 7519

- Claim Name: "exp"
- Claim Description: Expiration Time
- Change Controller: IESG
- Specification Document(s): Section 4.1.4 of RFC 7519

- Claim Name: "nbf"
- Claim Description: Not Before
- Change Controller: IESG
- Specification Document(s): Section 4.1.5 of RFC 7519

- Claim Name: "iat"
- Claim Description: Issued At
- Change Controller: IESG
- Specification Document(s): Section 4.1.6 of RFC 7519

- Claim Name: "jti"
- Claim Description: JWT ID
- Change Controller: IESG
- Specification Document(s): Section 4.1.7 of RFC 7519

```


# uuid_argon

## UUID Layouts

> 버전만 잘 선택하면 다 알아서 만들어주는 라이브러리가 있다
> 근데 어떤 버전을 사용할지에 대한 트레이드오프 고민하려면 일단 알긴 해야함

- 공통
    - ver : version (4bit, bits 48~51, octet 6 상위)
    - var : variant (2bit, bits 64~65, octet 8 상위 / 0b10 고정)

### UUIDv1

- UTC를 기반으로 100ns 간격으로 증가하는 60bit timestamp (1582-10-15 00:00:00.00 기준)
    - UTC를 사용할 수 없는 시스템은 일관되게 로컬 시간을 사용할 수 있으나 비권장 (타임존 오프셋만 있으면 UTC 생성 가능)
- 하위 비트(time_low)가 가장 앞에 배치되어 시간순 정렬이 불가능함

- Bit Layout
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           time_low                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           time_mid            |  ver  |       time_high       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|var|         clock_seq         |             node              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                              node                             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

- time_low
    - 60bit timestamp의 최하위(LSB) 32bit (bits 0~31, octets 0~3)

- time_mid
    - 60bit timestamp의 중간 16bit (bits 32~47, octets 4~5)

- time_high
    - 60bit timestamp의 최상위(MSB) 12bit (bits 52~63, octets 6~7)
    - 원문에는 least significant로 표기되어 있으나 most significant의 오타

- clock_seq
    - 클록이 과거로 돌아가거나 Node ID가 변경될 때 발생할 수 있는 중복을 방지하기 위한 14bit 필드 (bits 66~79, octets 8~9)
    - 시스템 수명 동안 최초 1회 반드시(MUST) Node ID와 무관한 난수로 초기화되어야 함
    - 시계가 과거로 설정되었거나 Node ID가 변경된 경우 반드시(MUST) 변경해야 함 (이전 값을 알면 1 증가 가능(MAY), 모르면 난수 또는 의사 난수로 설정(SHOULD))

- node
    - 48bit 공간적 고유 식별자 (bits 80~127, octets 10~15 / IEEE 802 MAC 주소 또는 난수)
    - 여러 개의 IEEE 802 주소가 있으면 아무거나 사용 가능(MAY)하며, 주소가 없으면 반드시(MUST) 난수/의사 난수 사용
    - 64bit MAC 주소 사용 시 가장 오른쪽의 최하위 48bit 사용 가능(MAY)
    - IEEE 802.15.4 16bit 주소 사용 시스템은 64bit MAC 주소의 최하위 48bit를 사용하거나(SHOULD), 16bit MAC 주소 끝에 32bit 난수를 붙여 48bit로 구성

### UUIDv2

- DCE 보안(DCE Security) UUID를 위한 버전 ([C309], [C311] 참조)
- 본 사양의 정의 범위를 벗어남

### UUIDv3

- 특정 namespace 내에서 고유한 name으로부터 UUID를 생성하기 위한 버전
- Namespace ID와 name을 해당 네임스페이스 규칙에 따라 네트워크 바이트 순서의 정규화된 옥텟 시퀀스로 변환 후 이어 붙여 MD5 해시(128bit)를 계산하고, ver와 var 비트를 대체함
- 가능한 경우 UUIDv3 대신 UUIDv5를 사용해야 함(SHOULD)

- Bit Layout
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                            md5_high                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          md5_high             |  ver  |       md5_mid         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|var|                        md5_low                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                            md5_low                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

- md5_high
    - 계산된 MD5 값의 최상위 48bit (bits 0~47, octets 0~5)

- md5_mid
    - md5_high 직후 이어지는 16bit 중 최하위 12bit (bits 52~63, octets 6~7 / 상위 4bit는 ver로 대체됨)

- md5_low
    - 계산된 MD5 값의 마지막 64bit 중 최하위 62bit (bits 66~127, octets 8~15 / 상위 2bit는 var로 대체됨)

### UUIDv4

- 완전한 난수(truly random) 또는 의사 난수(pseudorandom)로부터 UUID를 생성하기 위한 버전
- 128bit 난수를 생성해 채운 뒤 ver와 var 비트를 대체하거나, 필요한 비트 수(총 122bit)만큼만 난수를 생성한 뒤 ver와 var를 필요한 위치에 이어 붙일 수 있음(MAY)

- Bit Layout
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           random_a                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          random_a             |  ver  |       random_b        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|var|                       random_c                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           random_c                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

- random_a
    - 무작위 데이터로 채워지는 처음 48bit (bits 0~47, octets 0~5)

- random_b
    - 무작위 데이터로 채워지는 12bit (bits 52~63, octets 6~7)

- random_c
    - var 필드 직후 무작위 데이터로 채워지는 마지막 62bit (bits 66~127, octets 8~15)

### UUIDv5

- 특정 namespace 내에서 고유한 name으로부터 UUID를 생성하기 위한 버전
- Namespace ID와 name을 정규화된 옥텟 시퀀스(네트워크 바이트 순서)로 변환 후 이어 붙여 SHA-1 해시(160bit)를 계산함
    - 최상위 128bit만 사용하여 레이아웃을 채우고 나머지 최하위 32bit는 버린 뒤, ver와 var 비트를 대체함
- 보안 정책상 SHA-1을 사용할 수 없어 SHA-256 이상의 방식을 사용하려는 경우, 절대로(MUST NOT) UUIDv5를 사용해서는 안 되며 반드시(MUST) UUIDv8 공간 내에서 구현해야 함

- Bit Layout
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           sha1_high                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         sha1_high             |  ver  |      sha1_mid         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|var|                       sha1_low                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           sha1_low                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

- sha1_high
    - 계산된 SHA-1 값의 최상위 48bit (bits 0~47, octets 0~5)

- sha1_mid
    - sha1_high 직후 이어지는 16bit 중 최하위 12bit (bits 52~63, octets 6~7 / 상위 4bit는 ver로 대체됨)

- sha1_low
    - 남은 SHA-1 해시에서 최상위 2bit(var 자리)를 건너뛴 다음 이어지는 최상위 62bit (bits 66~127, octets 8~15 / 남은 32bit는 버려짐)

### UUIDv6

- DB 지역성(DB locality) 향상을 위해 타임스탬프 바이트가 최상위(MSB)부터 최하위(LSB) 순서로 저장되도록 재정렬한 UUIDv1의 필드 호환 버전
- 기존 UUIDv1이 사용되는 환경에서 주로 구현될 것으로 예상되며, 레거시 UUIDv1과 관련 없는 시스템은 대신 UUIDv7을 사용해야 함(SHOULD)
- 새로 생성되는 각 UUIDv6마다 clock_seq와 node 비트를 의사 난수 값으로 재설정해야 하나(SHOULD), 기존 UUIDv1의 클록 시퀀스 및 MAC 주소 동작을 유지할 수도 있음(MAY)

- Bit Layout
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           time_high                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           time_mid            |  ver  |       time_low        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|var|         clock_seq         |             node              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                              node                             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

- time_high
    - 60bit timestamp의 최상위(MSB) 32bit (bits 0~31, octets 0~3)

- time_mid
    - 60bit timestamp의 중간 16bit (bits 32~47, octets 4~5)
    - time_high와 time_mid의 48bit는 순서가 그대로 유지되므로 두 필드로 분할하는 단계는 선택 사항(OPTIONAL)이며, 기존 UUIDv1 구현체를 재사용할 때 유용함

- time_low
    - 60bit timestamp의 최하위(LSB) 12bit (bits 52~63, octets 6~7)

- clock_seq
    - 14bit 클록 시퀀스 (bits 66~79, octets 8~9 / UUIDv1과 위치 동일)

- node
    - 48bit 공간적 고유 식별자 (bits 80~127, octets 10~15 / UUIDv1과 위치 동일)

### UUIDv7

- Unix Epoch timestamp(윤초를 제외한 1970-01-01 00:00:00 UTC 이후의 밀리초 수)에서 파생된 시간 정렬(time-ordered) 값 필드를 특징으로 하는 버전
- 일반적으로 UUIDv1이나 UUIDv6보다 향상된 엔트로피 특성을 가지며, 가능한 경우 UUIDv1 및 UUIDv6 대신 UUIDv7을 활용해야 함(SHOULD)
- 최상위 48bit에 밀리초 단위의 Unix timestamp를 할당하고, ver와 var를 제외한 나머지 74bit를 난수로 채워 생성함
    - 대안으로 1ms 내에서의 추가적인 단조 증가성(monotonicity)을 보장하기 위해 나머지 74bit를 최상위 비트부터 다음 하위 필드들의 조합으로 채울 수 있음(MAY)
        1. 서브 밀리초 타임스탬프 소수점 값 (최대 12bit, OPTIONAL)
        2. 세심하게 시드(seed)가 설정된 카운터 (OPTIONAL)
        3. 남은 공간에 대해 새로 생성되는 각 UUIDv7마다 채워지는 무작위 데이터

- Bit Layout
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           unix_ts_ms                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          unix_ts_ms           |  ver  |       rand_a          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|var|                        rand_b                             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                            rand_b                             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

- unix_ts_ms
    - 밀리초 단위의 Unix Epoch timestamp를 나타내는 48bit big-endian 부호 없는 숫자 (bits 0~47, octets 0~5)

- rand_a
    - 고유성을 제공하기 위한 12bit 의사 난수 데이터 및/또는 추가적인 단조 증가성을 보장하기 위한 선택적 구조체 (bits 52~63, octets 6~7)

- rand_b
    - 고유성을 제공하기 위한 마지막 62bit 의사 난수 데이터 및/또는 추가적인 단조 증가성을 보장하기 위한 선택적 카운터 (bits 66~127, octets 8~15)

### UUIDv8

- 실험적 목적 또는 벤더 종속적인(vendor-specific) 사용 사례를 위한 포맷
    - 예: 문서 정의 외의 추가 정보를 UUID에 내장하거나, 애플리케이션/언어 제약으로 기존 UUID를 쓸 수 없는 경우 등
- ver와 var 비트의 설정만 강제(MUST)하며 나머지 122bit는 구현체가 자유롭게 정의
- 고유성은 구현에 따라 다르므로 보장된다고 가정해서는 안 되며(MUST NOT), 122bit를 난수로 채우는 UUIDv4의 대체품이 아님

- Bit Layout
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           custom_a                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          custom_a             |  ver  |       custom_b        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|var|                       custom_c                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           custom_c                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

- custom_a
    - 구현체가 적절하다고 판단하는 대로 채울 수 있는 처음 48bit (bits 0~47, octets 0~5)

- custom_b
    - 구현체가 적절하다고 판단하는 대로 채울 수 있는 12bit (bits 52~63, octets 6~7)

- custom_c
    - var 필드 직후 구현체가 적절하다고 판단하는 대로 채울 수 있는 마지막 62bit (bits 66~127, octets 8~15)

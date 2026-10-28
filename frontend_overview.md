# 프론트엔드에 대한 이야기

> 당장 웹을 만들어야한다면 `html/css/js`도 넘기고 `typescript`와 `react`를 기반으로 한 프레임워크를, 앱을 만들어야한다면 쓸데없이 네이티브 관심 두지 않고 `cross-platform`인 `flutter`를 통해 llm에게 지시하면 된다. (component기반으로 화면을 정의하며 개발할 수 있게 지원해줘서 직접 이해하고 구성하기도 쉽다)
> 다만 나에겐 부족하기에 최대한 여러 요소가 한눈에 들어오게 다시 정리하고자 한다

## 분류하기 복잡한 기본 지식

> 정확히는 분류를 실패한 잡다한 지식이다
> 몰라도 개발할 수 있겠지만 이정도 수준도 놓치면 이 위에 있는 웹과 앱을 내가 설명할 수가 없었다


- client가 직접 상호작용하는 영역으로서 크게 3가지 ui를 가지고 있다. 42출신이면 못 다루는 사람이 없는 `cli`, `tui`, 그리고 개발 안배워도 항상 보고 사는 `gui`.

- `command line interface`는 `terminal`(단말)에서 `command line`(명령줄)을 통해 다룬다. 명령줄을 해석하는 프로그램을 `shell`이라고 하는데, 리눅스에서는 bash, 맥에서는 zsh가 주로 보인다. (경량화의 끝판왕 alpine은 sh를 쓴다) cli에서도 웹 접근이 가능은 하지만 실질적으로 사용성이 좋지 않아 사람이 잘 활용하지는 않는다. (`curl`같은 프로그램을 활용해서 llm이 검색하는 모습을 확인해 봤을 수 있을것이다.) 
- `text user interface`는 따로 존재하는 것이 아니라 cli에서 화살표, 단축키 등을 활용해 제어 가능하게 만든 것이다. os를 설치할 때 나오는 마우스가 없어도 되는 그 인터페이스이기도 하고 aptitude나 vim, nano같은 여러 형태로 존재한다.
- `graphic user interface`는 터치, 마우스 기반의 사용자 인터페이스다. OS는 `Desktop`에선 `Linux` `Window` `MacOS`, `mobile`환경에선 `android`, `ios`, `ipados`가 대표적이다 (안드로이드는 태블릿 ui를 대충 지원해주고 끝낸다.)


- os를 설치할 때 이미지의 용량과 권장사양을 보면 `cli`와 `gui`의 차이가 몇배 이상 난다는 부분을 확인할 수 있다.
    - on-premise에서도 off-premise에서도 gui로 운영하는 순간 그 자원이 낭비된다는 부분을 알 수 있다.
    - cli를 기반으로 한 linux를 설치할 때도 각 linux os마다 최소, 권장사양 차이가 심하다
    - alpine이 가장 경량화되어있어 cloud에서 alpine linux를 기반으로 커스터마이징해 제공하기 때문에 이미지의 이름을 보면 alpine이 적혀있는 경우가 많이 보인다.

`cli`, `tui`환경에서 사용할 수 있는 프로그램들은 일반적으로 내장 라이브러리만으로 충분히 만들 수 있지만 `gui`의 경우 각 `OS`마다 프로그램을 만들기 위한 라이브러리와 프레임워크가 다르게 제공되어있다.

- 42에서 간단하게 활용 가능한 `mlx`(llm과 관계 없는데 약자가 겹쳤다)는 `pixel`을 기반으로 화면을 구성한다.
    - [42의 `mlx`(MiniLibX) 실습 가이드](https://harm-smits.github.io/42docs/)
    - 각 `pixel`의 `TRGB`를 지정해 화면을 구성하거나 임의의 범위를 `.xpm`으로 출력할 수 있다.
        - `big endian`환경에서 4byte int에 `0x00ffffff`를 선언하고 1 byte 단위로 접근하면 `0x00`, `0xff`, `0xff`, `0xff` 형태로 나온다.
        - `little endian`에서 4byte int에 `0x00ffffff`를 선언하고 1 byte 단위로 접근하면 `0xff`, `0xff`, `0xff`, `0x00` 형태로 나온다.
        - mlx의 경우 `mlx_get_data_addr`에서 endian 정보를 반환한다. 이 정보를 기반으로 분기를 나누면 된다.
        - [직접 확인해보기](#엔디안_확인해보기)
        - int 단위로만 개발할 땐 문제가 생길 수 없지만 확인된 엔디안으로 분기 없이 byte 연산자를 사용하도록 개발한다면 문제가 생긴다.
            - 다른 엔디안을 사용하는 OS에서 발생하는 문제는 사실 지금 시점에선 보기 어렵다. 리눅스도 맥도 윈도우도 리틀 엔디안을 사용한다. (라즈베리 파이, 아두이노, ESP32 등의 유명한 하드웨어도 그렇다.)


- native gui 개발의 예
    - Desktop
        - `Window` : C# 기반으로 visual studio를 통해 window form app 개발 가능
        - `MacOS` : swift기반으로 xcode를 통해 개발 가능
        - `Linux` : C, python 기반으로 GTK, C++ 기반으로 Qt를 사용해 개발 가능
    - Mobile
        - `Android` : kotlin기반으로 android studio를 통해 개발 가능
        - `iOS / iPadOS` : swift기반으로 xcode를 통해 개발 가능




- web browser
    - URI 중 URL을 해석할 줄 안다
    - html, css, js를 해석해 화면을 출력한다
    - L4(tcp, udp)계층을 직접적으로 사용할 수 없다
    - http/https기반의 URL만 해석할 수 있다
    - http/https를 기반으로 ws/wss를 통해 웹 소켓 연결이 가능하다
        - 새로운 표준 프로토콜을 추가하는 것이 비용이 커서 기존 프로토콜을 기반으로 만들어졌다
        - 실시간 통신의 경우 http로는 사실상 불가능하고 web socket을 사용해야만 한다
            - 채팅, 영상, 게임 등의 서비스에서 지연을 크게 줄여준다
    - cookie와 web storage를 이용해 클라이언트의 정보를 직접 저장 및 관리한다
    

- `network io`
    - 문서, 사진 등의 정적 파일을 받아오는 경우 (html, css, js등의 웹 문서나 이미지, 영상, 압축된 파일 등)
    - 영상 등의 실시간 스트리밍
    - 게임처럼 클라이언트에 설치된 프로그램 내부에 이미지, 사운드파일이 저장되어있어 서버에서 어떤 파일을 사용해야하는지를 알려주는 경우
    - http api
        - RESTful한 경우에만 REST api라고 불려야한다
            - 사실 다들 안지켜서 자료 검증을 정말 잘 해야한다...
    - ecole42의 ft_transcendence에서 pong game을 위해 사용하는 websocket도 있다

- `cross-platform`
    > web, app을 둘 다 개발할 수 있는 라이브러리, 프레임워크
    > 둘 중 하나가 메인이라서 서브 플랫폼에서 단점이 존재한다
    > (소규모 프로젝트에선 성능상 불이익이 작다.)
    - `react` : web이 메인 플랫폼인 라이브러리
        - 라이브러리인만큼 개발자가 직접 필요한 모든것을 가져와 적절하게 사용할 줄 알아야한다
        - `next.js`라는 `react`기반 프레임워크도 있다
            - 서버측의 dir tree를 기반으로 url을 만들어 라우팅을 해준다
    - `flutter` : app이 메인 플랫폼인 프레임워크
        - `DOM` 없이 `Canvas`에 직접 렌더링해서 `SEO`가 기본적으로는 불가능하다
            - app이 일반적인 검색 엔진에서 나올 필요가 정말 있나?
            - 일반적인 웹페이지처럼 자연스럽게 가능한게 아닐뿐이지 메타데이터를 제공하는 것 자체는 여러 도구로 가능하다
        - 서버와 api를 통해 통신하는 경우 해당 기능은 `Riverpod`으로 관리해야한다
            - 다른 것도 있는데 저게 가장 우선시된다

---


## web

### basic
- html
- css
- js


### library

> 내 프로젝트에서 직접 가지고 있을 수도 있고, cdn으로도 가져올 수 있다

- css library
    - bootstrap
    - tailwind css
- js library
    - Three.js


## app

### native

#### android

#### ios / ipados


## cross-platform



---

> 일단 정리 포기하고 작성부터

- `ui`
    - `cli`
    - `tui`
    - `gui`

- `os`
    - `linux`
    - `window`
    - `macos`
    - `android`
    - `ios`

- `platform`
    - `web`
    - `cross-platform`
    - `native`

- `application`
    - `desktop`
    - `mobile`
    - `embedded`

- `UIUX`
    - ???


---

# 엔디안_확인해보기
```C
#include <unistd.h>

int main(void)
{
    int a;

    a = 0x41424344;
    write(1, &a, 4);
    write(1, "\n", 1);
    return (0);
}
```
`little endian` 환경 실행결과: `DCBA`
`big endian` 환경 실행결과: `ABCD`
```shell
~/backend_study/test_project_kt_sb (main*) » ./a.out       jeongjinseok@Jeongui-Macmini
DCBA
```

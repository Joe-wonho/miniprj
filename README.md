# 같이 보실? 

현재 상영중인 영화를 장르 별로 보고 후기를 적으세요!



# 프로젝트 기간 및 팀소개

#### 프로젝트 기간 : 2021-09-13 ~ 2021-09-17

#### 팀 소개 :

- 팀장:

  - 조원호 

    `[JWT] sign in/up, logout part code`   ` [JWT] 사용자가 쓴 후기만 조회`  `[mongoDB] Delete reviews using ObjectId` `[ajax] profile part code` `[html/css] login page` `[html/css] detail page (support)` `[ajax] index, detail page part code(support)`

- 팀원:

  - 구산하

    `[bs4] Naver Movie crawling` `[ajax] index, detail page & profile Update part code`

    `[UI] index page ` `[html/css] profile page (support)`  `[mongoDB] DB structure design&application`

    

  - 신유빈

    `[html/css] index, detail profile page ` `[html/css] detail page` `[html/css] pofile page` 

  - 하진수

    `[html/css] index page` `[html/css] detail page` 



# 기술 스택

- bs4

- mongoDB

- jinja2

- Flask

- JWT

- ajax

- AWS EC2

  

# CRUD

### Create

| process                                             |        DB        |  page  |
| :-------------------------------------------------- | :--------------: | :----: |
| 회원가입시 받은 사용자의 정보를 DB에 저장           |   ```users```    | index  |
| 크롤링한 영화 데이터를 DB에 저장                    | ```movie_info``` |   -    |
| 사용자가 작성한 후기를 사용자 정보와 함께 DB에 저장 |  ```posting```   | detail |

### Read

| process                                            |        DB        |  page   |
| :------------------------------------------------- | :--------------: | :-----: |
| 후기가 많은 영화, 장르별 영화 리스트를 DB에서 조회 | ```movie_info``` |  index  |
| 사용자가 선택한 영화의 정보를 DB에서 조회          | ```movie_info``` | detail  |
| 영화에 작성된 후기 리스트를  DB에서 조회           |  ```posting```   | detail  |
| 현재 접속한 사용자가 작성했던 후기들을 DB에서 조회 |  ```posting```   | profile |

### Update

| process                              |        DB        |  page   |
| :----------------------------------- | :--------------: | :-----: |
| 후기가 작성될 때 후기 수 카운트 증가 | ```movie_info``` | datail  |
| 프로필 닉네임과 소개 수정            |   ```users```    | profile |

### Delete

| process                     |      DB       |  page   |
| :-------------------------- | :-----------: | :-----: |
| 사용자가 작성한 게시글 삭제 | ```posting``` | profile |



# 개인회고

``조원호`` - https://velog.io/@whdnjsgh22/WEEK-1-%ED%9A%8C%EA%B3%A0%EB%A1%9D-WIM

`구산하` - https://github.com/9sanha/TIL/blob/main/21-09-17.md

`신유빈` - 

`하진수` - 


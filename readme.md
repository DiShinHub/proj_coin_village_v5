# 코인빌리지 버전 5 (작성 중)  

### 소스 설치 순서 

#### API 키 설정
<pre>
[Upbit Open API Guide](https://upbit.com/service_center/open_api_guide)  
[Binance API](https://www.binance.com/en/binance-api)
</pre>

#### Git 클론
<pre>
git clone https://github.com/DiShinHub/proj_coin_village_v5
</pre>

#### Docker 설치
<pre>
https://www.docker.com/
</pre>

#### 배치 파일을 사용하여 빌드
<pre>
./_ascm/bat/cv-docker-compose-build.bat
</pre>

#### 기본 DB 초기화
<pre>
./_ascm/bat/cv-postgres-init.bat
</pre>

#### 소스 실행
<pre>
./_ascm/bat/cv-docker-compose-reload.bat
</pre>


### 폴더 트리

<pre>
📦 proj_cv5
├── 📂 _ascm                            # 소스 컨트롤 오토메이션 
├── 📂 apps                             # 앱
│   ├── 📂 scheduler                    # 스케쥴러 앱
│   │   ├── 📂 dao                      # 다오
│   │   │   └──{dao}.py
│   │   ├── 📂 core                     # 코어
│   │   │   └──{core}.py
│   │   ├── 📂 service                  #
│   │   │   ├── {service}_{version}.py
│   │   │   └── {service}_{version}.py
│   ├── 📂 task_worker                  # 테스크 워커 앱
│   │   ├── 📂 dao
│   │   │   └──{dao}.py
│   │   ├── 📂 core
│   │   │   └──{core}.py
│   │   ├── 📂 service
│   │   │   ├── {service}_{version}.py
│   │   │   └── {service}_{version}.py
├── 📂 docker
├── 📂 docker-compose
├── 📂 shares # 공용 파일
│   ├── 📂 config
│   ├── 📂 decorations
│   ├── 📂 functions
│   └── 📂 modules
├── .gitignore                  # Git 제외 파일
├── .git                        # Git 
├── poetry.lock                 # 의존성 관리
├── pyproject.toml              # 의존성 관리 
└── readme.md                   # 프로젝트 개요

</pre>


<h3>
코인빌리지 버전 5 프로젝트 
</h3>

<h3>
folder tree
</h3>

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
# Automated Source Control Management  

### 소스 설치 순서 (보강 중)  

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
./cv-docker-compose-build.bat
</pre>

#### 기본 DB 초기화
<pre>
./cv-postgres-init.bat
</pre>

#### 소스 실행
<pre>
./cv-docker-compose-reload.bat
</pre>
# Automated Source Control Management  

### 소스 설치 순서


<pre>
1. **API 키 설정** (보강 중)  
[Upbit Open API Guide](https://upbit.com/service_center/open_api_guide)  
[Binance API](https://www.binance.com/en/binance-api)
</pre>
<pre>
2. **Git 클론**  
git clone https://github.com/DiShinHub/proj_coin_village_v5
</pre>
<pre>
3. Docker 설치
https://www.docker.com/
</pre>
<pre>
4. 배치 파일을 사용하여 빌드
./cv-docker-compose-build.bat
</pre>
<pre>
5. 기본 DB 초기화
./cv-postgres-init.bat
</pre>
6. 소스 실행
./cv-docker-compose-reload.bat
</pre>
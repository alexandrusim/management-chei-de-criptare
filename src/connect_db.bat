@echo off
echo Se conecteaza la containerul talent-bridge-db...

:: Comanda de mai jos intra in container si ruleaza direct mariadb pe baza de date specificata
docker exec -it MariaDB-SI mariadb -u root -p

:: Aceasta linie tine fereastra deschisa in caz de eroare, dupa ce iesi din DB
pause
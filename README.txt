MOVE CLOCK v2 · iPhone용 운동 타이머 웹앱

접속: https://youheewon.github.io/move-clock/
GitHub: https://github.com/youheewon/move-clock

기능
- 운동 루틴 직접 만들기/편집/삭제: 아이폰의 localStorage에 저장
- 사진 속 어깨·상체 8동작 프리셋 추가(각각 1세트, 휴식 20초)
- 운동 순서/진행률/현재 운동·세트/다음 운동을 한눈에 표시
- 휴식 시작: 단일 전자 비프음 '삡!'
- 운동 시작: 이중 전자 비프음 '삐빅!'
- 휴식 종료 전 5, 4, 3, 2, 1 한국어 음성 안내
- Supertonic 3 여성 F1 / 남성 M1 음성 선택 및 기본 iPhone 음성 대체 모드
- 효과음 및 음성 각각 켜기/끄기
- Safari '홈 화면에 추가'로 사용 가능, 애플 단축어 URL 열기로 연동 가능

AI 음성 파일 동작 구조
- 앱은 Supertonic 모델 자체를 다운로드하지 않습니다.
- 사전에 생성된 짧은 WAV 음성들을 voices/female/ 및 voices/male/에 저장해 재생합니다.
- 앱 화면의 음성 선택에서 여성/남성을 자유롭게 변경할 수 있습니다.
- 미리 생성된 파일이 아직 없다면 아이폰 기본 TTS로 대신 안내합니다.
- 처음 웹앱을 열 때 일부 음성 파일을 미리 받아 캐시합니다.
- GitHub Actions의 'Build Korean Supertonic voices'가 두 음성 세트를 자동으로 만듭니다.
- 수동 실행이 필요하다면 Windows에서 run_generate_voices_windows.bat 사용.
- 음성 파일은 GitHub Actions 작업이 성공하여 저장소에 반영된 이후 사용 가능합니다.
- 모델 출처 https://github.com/supertone-oss-archive/supertonic-py
- 모델 라이선스 OpenRAIL-M (사용 제한과 저작자 표기 준수 필요)

배포
1. GitHub 저장소 Settings > Pages
2. Source 'Deploy from a branch' 선택
3. Branch main / root (/) 선택
4. https://youheewon.github.io/move-clock/ 에서 새로고침
5. iPhone Safari에서 공유 > 홈 화면에 추가
6. 기존 홈 화면 웹앱을 썼다면 최신 코드가 로드되도록 재실행

단축어 예시 URL
https://youheewon.github.io/move-clock/?routine=shoulder8

주의
- iOS에서 화면을 잠그거나 다른 앱으로 전환하면 웹 오디오/타이머가 제한될 수 있습니다.
- 휴식 비프와 AI 음성은 '소리 테스트' 버튼을 눌러 실제 아이폰에서 확인하세요.
- 로컬 저장 데이터는 Safari 데이터 삭제 시 사라질 수 있습니다.
- 개인 커스텀 운동명에 해당하는 AI 클립이 없는 경우 일반적인 '운동 시작' 음성이 대신 나옵니다.

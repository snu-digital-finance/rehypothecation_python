import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# 여러 CSV 파일을 순차적으로 읽기
df_list = []
for filename in [
    'download-query-results-9ff20136-4acd-485e-b26e-a39ae68c8b92 (1).csv',
    'download-query-results-9ff20136-4acd-485e-b26e-a39ae68c8b92 (2).csv',
    'download-query-results-9ff20136-4acd-485e-b26e-a39ae68c8b92.csv',
    'download-query-results-efd8d74c-e583-48ec-b3ae-4a0e66f1b4fb.csv'
]:
    try:
        df = pd.read_csv(filename)
        df_list.append(df)
    except Exception as e:
        print(f"{filename} 읽기 실패: {str(e)}")

# 데이터프레임 결합
if df_list:
    df = pd.concat(df_list, ignore_index=True)
else:
    print("데이터 로드 실패: 모든 파일을 읽을 수 없습니다.")
    exit()

# 타임스탬프 처리 (개선된 버전)
def clean_timestamp(ts):
    # 불필요한 문자 제거
    ts = str(ts).strip()
    # 빈 문자열 처리
    if not ts or ts == "﻿":
        return pd.NaT
    return ts

# 타임스탬프 정리 및 변환
df['BLOCK_TIMESTAMP'] = df['BLOCK_TIMESTAMP'].apply(clean_timestamp)
df['BLOCK_TIMESTAMP'] = pd.to_datetime(df['BLOCK_TIMESTAMP'], 
                                      errors='coerce',
                                      format='mixed')

# 타임스탬프 변환 결과 확인
print("\n타임스탬프 변환 통계:")
print(f"전체 행 수: {len(df)}")
print(f"유효한 타임스탬프 수: {df['BLOCK_TIMESTAMP'].notna().sum()}")
print(f"유효하지 않은 타임스탬프 수: {df['BLOCK_TIMESTAMP'].isna().sum()}")

# 나머지 코드는 동일하게 유지
# 주요 통계량 계산
stats = {
    '거래량': df['AMOUNT'].sum(),
    '거래 횟수': df['TX_HASH'].nunique(),
    '유니크 주소 수': df['ACCOUNT'].nunique(),
    '유니크 토큰 수': df['TOKEN'].nunique(),
    '유니크 이벤트 수': df['EVENT'].nunique()
}

print("\n데이터 통계:")
for key, value in stats.items():
    print(f"{key}: {value}")

# 시간별 거래량 분석
daily_volume = df.groupby(df['BLOCK_TIMESTAMP'].dt.date)['AMOUNT'].sum().reset_index()
daily_volume.columns = ['날짜', '거래량']

# 시각화
plt.figure(figsize=(15, 10))

# 1. 일별 거래량 그래프
plt.subplot(2, 2, 1)
plt.plot(daily_volume['날짜'], daily_volume['거래량'], marker='o')
plt.title('일별 거래량 추이')
plt.xlabel('날짜')
plt.ylabel('거래량')
plt.xticks(rotation=45)
plt.grid(True)

# 2. 토큰별 거래량 분포
plt.subplot(2, 2, 2)
token_volume = df.groupby('TOKEN')['AMOUNT'].sum().sort_values(ascending=False)
plt.bar(token_volume.index[:10], token_volume.values[:10])
plt.title('토큰별 거래량 TOP 10')
plt.xlabel('토큰')
plt.ylabel('거래량')
plt.xticks(rotation=45)
plt.grid(True)

# 3. 이벤트 유형 분포
plt.subplot(2, 2, 3)
event_counts = df['EVENT'].value_counts()
plt.pie(event_counts.values[:5], labels=event_counts.index[:5], autopct='%1.1f%%')
plt.title('이벤트 유형 분포 (TOP 5)')

# 4. 주소별 거래량 분포
plt.subplot(2, 2, 4)
account_volume = df.groupby('ACCOUNT')['AMOUNT'].sum().sort_values(ascending=False)
plt.bar(account_volume.index[:10], account_volume.values[:10])
plt.title('주소별 거래량 TOP 10')
plt.xlabel('주소')
plt.ylabel('거래량')
plt.xticks(rotation=45)
plt.grid(True)

plt.tight_layout()
plt.show()

# 상세 분석
print("\n토큰별 통계:")
token_stats = df.groupby('TOKEN').agg({
    'AMOUNT': ['sum', 'mean', 'count'],
    'ACCOUNT': 'nunique'
}).round(2)
print(token_stats)

print("\n이벤트별 통계:")
event_stats = df.groupby('EVENT').agg({
    'AMOUNT': ['sum', 'mean', 'count'],
    'ACCOUNT': 'nunique'
}).round(2)
print(event_stats)
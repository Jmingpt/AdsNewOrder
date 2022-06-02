import pandas as pd
import warnings
warnings.filterwarnings("ignore")

#----------------------------function----------------------------#
def menu(campaign):
    if 'PT(S)' in campaign:
        return '1-Google Ads'
    elif 'Smart Shopping' in campaign:
        return '2-Google Shopping Ads'
    elif 'PT(D)' in campaign and 'Discovery' not in campaign:
        return '3-Google Display Network'
    elif 'PT(D)' in campaign and 'Discovery' in campaign:
        return '4-Google Discovery Network'
    elif 'PT - ' in campaign and 'Performance Max' in campaign:
        return '5-Google Performance Max'
    elif 'PT - YouTube' in campaign and 'MKT' not in campaign:
        return '6-YouTube Ads'
    elif 'PT - ' in campaign:
        return '7-Facebook Ads'
    else:
        return 'Other'

def detail(campaign):
    if 'Branded Keywords' in campaign:
        return '1-Brand keywords'
    elif 'Remarketing' in campaign:
        return '3-Retargeting'
    elif 'Prospecting' in campaign:
        return '4-Non-retargeting'
    elif 'prospecting' in campaign:
        return '4-Non-retargeting'
    else:
        return '2-Non-brand keywords'

def class_ab(detail):
    if 'Non-' in detail:
        return 'B'
    else:
        return 'A'

def purpose(cls_ab):
    if cls_ab == 'A':
        return 'Short-term sales'
    else:
        return 'New potential customers (Investing in the Future)'

def kpi(cls_ab):
    if cls_ab == 'A':
        return 'ROAS'
    else:
        return 'CPA'
#----------------------------function----------------------------#


def report_trans(df_fb, df_ga, df_gads):
            
    df_gads['Campaign ID'] = df_gads['Campaign ID'].astype(str)
    df_g = pd.merge(df_ga, df_gads, how='left', on=['Campaign ID', 'Date'])
    df_gg = df_g[df_g['Source'] == 'google']
    df_gf = df_g[df_g['Source'] == 'uqmy_facebook']
    
    medium = []
    source = []
    campaign = []
    for tag in df_fb['URL tags']:
        if tag != 'No url tag':
            temp = tag.split('&')
            if len(temp) <= 5:
                for i in temp:
                    if 'medium' in i:
                        medium.append(i.split('=')[1])
                    elif 'source' in i:
                        source.append(i.split('=')[1])
                    elif 'campaign' in i:
                        campaign.append(i.split('=')[1])
            else:
                corr_camp = []
                for j in temp:
                    if j.startswith('utm_campaign') or not j.startswith('utm_'):
                        corr_camp.append(j)

                new_camp = "&".join(corr_camp)
                del temp[2]
                del temp[2]
                temp.append(new_camp)
                for k in temp:
                    if 'medium' in k:
                        medium.append(k.split('=')[1])
                    elif 'source' in k:
                        source.append(k.split('=')[1])
                    elif 'campaign' in k:
                        campaign.append(k.split('=')[1])
                        
        else:
            medium.append('No url tag')
            source.append('No url tag')
            campaign.append('No url tag')

    df_fb['Medium'] = medium
    df_fb['Source'] = source
    df_fb['Campaign'] = campaign
    
    df_fb = df_fb.groupby(['Date', 'Medium', 'Source', 'Campaign', 'Campaign name']).sum().reset_index()
    df_gf = df_gf.drop(columns=['Revenue', 'Cost', 'Conversions'])
    
    df_f = pd.merge(df_fb, df_gf, on=['Date', 'Campaign', 'Source', 'Medium'], how='left')
    df_f = df_f.drop(columns='Campaign')
    df_f = df_f.rename(columns={'Campaign name': 'Campaign', 'Conversion': 'Conversions'})
    df_f1 = df_f[['Date', 'Campaign ID', 'Campaign', 'Source', 'Medium', 'Sessions', 'Users', 'New Users', 'Revenue', 'Cost', 'Conversions']]
    
    df = pd.concat([df_gg, df_f1], ignore_index=True)
    df['Sessions'] = df['Sessions'].fillna(0)
    df['Users'] = df['Users'].fillna(0)
    df['New Users'] = df['New Users'].fillna(0)
    df['Revenue'] = df['Revenue'].fillna(0)
    df['Cost'] = df['Cost'].fillna(0)
    df['Conversions'] = df['Conversions'].fillna(0)
    
    df['Menu'] = df['Campaign'].apply(menu)
    df['Detail'] = df['Campaign'].apply(detail)
    df['Class'] = df['Detail'].apply(class_ab)
    df['Purpose'] = df['Class'].apply(purpose)
    df['KPI'] = df['Class'].apply(kpi)
    
    df = df[['Class', 'Purpose', 'KPI', 'Medium', 'Source', 'Menu', 'Detail', 'Cost', 'Sessions', 'Users', 'New Users', 'Conversions', 'Revenue']]
    df = df.groupby(['Class', 'Purpose', 'KPI', 'Medium', 'Source', 'Menu', 'Detail']).sum().reset_index()
    df = df.sort_values(by=['Menu', 'Source']).reset_index(drop=True)
    
    filter1 = (df['Source'] != 'google') | (df['Menu'] != '6-Facebook Ads')
    filter2 = (df['Detail'] != '2-Non-brand keywords') | (df['Menu'] != '6-Facebook Ads')

    df = df[filter1]
    df = df[filter2]
    df = df.reset_index(drop=True)
    
    for i in range(df.shape[0]):
        if 'Google Ads' in df['Menu'][i] and df['Medium'][i] == 'cpc':
            df['Medium'][i] = 'SEM'
        elif 'Google Shopping Ads' in df['Menu'][i] and df['Medium'][i] == 'cpc':
            df['Medium'][i] = 'SEM'
        elif df['Medium'][i] == 'affiliate':
            df['Medium'][i] = 'Affiliate'
        else:
            df['Medium'][i] = 'Display'

    for i in range(df.shape[0]):
        if df['Source'][i] == 'google':
            df['Source'][i] = 'Google'
        elif df['Source'][i] == 'uqmy_facebook':
            df['Source'][i] = 'Facebook'
        else:
            df['Source'][i] = 'No url tag'
            
    df = df.rename(columns={'Medium': 'Channel', 'Source': 'Media'})
    df = df.drop(df.index[df['Media'] == 'No url tag'])
    
    df = df.replace({  
        '1-Google Ads': 'Google Ads', 
        '2-Google Shopping Ads': 'Google Shopping Ads', 
        '3-Google Display Network': 'Google Display Network', 
        '4-Google Discovery Network': 'Google Discovery Network', 
        '5-Google Performance Max': 'Google Performance Max',
        '6-YouTube Ads': 'YouTube Ads', 
        '7-Facebook Ads': 'Facebook Ads', 
        '1-Brand keywords': 'Brand keywords', 
        '2-Non-brand keywords': 'Non-brand keywords', 
        '3-Retargeting': 'Retargeting', 
        '4-Non-retargeting': 'Non-retargeting'
    })
    
    df1 = df.copy()
    df1['Conversion Rate (%)'] = df1['Conversions']/df1['Sessions']*100
    df1['CPA'] = df1['Cost']/df1['Conversions']
    df1['ROAS (%)'] = df1['Revenue']/df1['Cost']*100

    df1['Cost (%)'] = df1['Cost']/df1['Cost'].sum()*100
    df1['New Users Ratio (%)'] = df1['New Users']/df1['Users']*100
    
    df1 = df1[['Class', 'Purpose', 'KPI', 'Channel', 'Media', 'Menu', 'Detail', 'Cost', 
               'Cost (%)', 'Sessions', 'Users', 'New Users', 'New Users Ratio (%)', 
               'Conversions', 'Conversion Rate (%)', 'CPA', 'Revenue', 'ROAS (%)']]
    
    return df1

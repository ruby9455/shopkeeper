import streamlit as st
import pandas as pd
from datetime import datetime

girl_dict = {
    '士':['千仞雪', '堇書', '花魁', '采詩官', '驛使', '馬湘蘭', '郡主', '棋士', '少將軍', '醫師', '尼姑' ,'小師姐', '舞女', '書香女', '精衛', '霓凰郡主', '伽羅奢', '小鹿女'],
    '農':['古國公主','苗疆聖女', '西湖船孃', '極夜', '紫玉', '馴馬師', '李香君', '花無缺', '牛郎', '乳娘', '小乞丐', '丫鬟', '採藥女', '女媧', '王后婦妤', '沈眉莊', '舞姬'],
    '工':['蘿','花郎', '小木匠', '董小宛', '花郎', '元宵姑娘', '豆腐女', '蹴鞠女', '針線女', '女魁', '塗山氏' ,'玉兔', '手工少女', '玩具職人','捉鬼師', '織女', '靈夜貓女', '花藝師', '新娘之妹'],
    '商':['小蝴蝶','馴鷹少女', '糖蘋果', '卞玉京', '新娘', '檳榔女', '西域女子', '琵琶女', '戲子', '賣傘女', '貴公子', '甄環', '墨璃', '秋螢', '南宮婉', '荒野鈴蘭', '織田市', '狐妖掌櫃'],
    '俠':['小師妹','小舞', '邀影', '市舶使', '漁歌', '巫女', '寂白門', '紅倌娘子', '浪子', '將門女子', '密探', '薩滿', '草原女孩', '獵人', '刺客', '嫦娥', '吳邪', '捕快']
}

buildings_list = ['翠竹居','蓮葉居', '萱草居','紫藤居','稻香居','蒲葦居','蘭草居',
             '梅花閣','牡丹閣','芙蓉閣','丹桂閣','茉莉閣','海棠閣','玫瑰閣',
             '春水軒','夏蓮軒','秋月軒','冬雪軒','月華軒','晨曦軒']

# Create an empty DataFrame
df = pd.DataFrame({
    '建築': buildings_list,
    '應援物數量': [None] * len(buildings_list),
    '美女': [None] * len(buildings_list),
    '職業': [None] * len(buildings_list)
})

def get_key_by_value(dictionary: dict, target_value: str):
    for key, values in dictionary.items():
        if target_value in values:
            return key
    return None

def cal_music_workshop(df):
    total_sums = {}
    for index, row in df.iterrows():
        selected_girl = row['美女']
        profession = get_key_by_value(girl_dict, selected_girl)
        quantity = int(row['應援物數量']) if str(row['應援物數量']).isdigit() else 0  # Convert input to integer, default to 0 if not a digit
        total_sums[profession] = total_sums.get(profession, 0) + quantity

    return total_sums
        
def suggest_music_workshop():
    # Retrieve the latest DataFrame and target professions from the session state
    df = st.session_state.user_input['df']
    target_professions = st.session_state.user_input['target_professions']
    
    # Step 1: Calculate the sum of 應援物
    total_sums = df.groupby('職業')['應援物數量'].sum().to_dict()
    
    # Step 2: Sort 建築 based on 應援物數量 in descending order
    sorted_buildings = df.sort_values(by='應援物數量', ascending=False)['建築'].tolist()

    # Step 3: Determine the minimum number of rows for non-target professions
    min_rows_non_target = 3
    
    # Step 4: Suggest changes to 職業 based on the criteria
    changes_needed = {}
    for building in sorted_buildings:
        row = df[df['建築'] == building].iloc[0]
        current_profession = row['職業']

        # Check if the profession is in the target list
        if current_profession not in target_professions:
            if current_profession not in changes_needed:
                changes_needed[current_profession] = {'count': 1, 'buildings': [building]}
            else:
                changes_needed[current_profession]['count'] += 1
                changes_needed[current_profession]['buildings'].append(building)
    
    # Distribute the rows of 建築 with the highest 應援物 to the target_professions evenly
    for target_profession in target_professions:
        if target_profession in changes_needed:
            target_count = total_sums.get(target_profession, 0)
            buildings_to_change = changes_needed[target_profession]['buildings']
            num_buildings_to_change = len(buildings_to_change)

            # Ensure minimum number of rows for non-target professions
            if changes_needed[target_profession]['count'] < min_rows_non_target:
                buildings_to_change.extend(sorted_buildings[num_buildings_to_change:num_buildings_to_change + min_rows_non_target - changes_needed[target_profession]['count']])

            # Distribute evenly
            num_buildings_to_change = len(buildings_to_change)
            for i, building in enumerate(buildings_to_change):
                df.loc[df['建築'] == building, '職業'] = target_profession

                # Update 應援物數量 if needed
                if i < target_count % num_buildings_to_change:
                    df.loc[df['建築'] == building, '應援物數量'] += 1
            
            # Mark the changed 職業 with a new column
            df.loc[df['職業'].isin(target_professions), 'Changed'] = True
            
    return df

def make_suggestion(df):
    user_input = st.session_state.user_input
    hate_professions = user_input.get('hate_professions', [])
    target_professions = user_input.get('target_professions', [])
    
    threshold = len(df) - 3*len(hate_professions) - 4*(5-len(hate_professions)-len(target_professions))

    tools_rank = {}
    occupation_len = {}
    actual_idx = {} # actual location
    for idx, row in df.iterrows():
        occupation = row['職業']
        if occupation not in actual_idx:
            actual_idx[occupation] = [idx]
            tools_rank[occupation] = [tool_nums.index(row['應援物數量'])]
            occupation_len[occupation] = 1
        else:
            actual_idx[occupation].append(idx)
            tools_rank[occupation].append(tool_nums.index(row['應援物數量']))
            occupation_len[occupation] += 1
    # st.write(tools_rank, occupation_len, actual_idx)

    df = df.sort_values(by=['應援物數量', '職業'], ascending=[False, True])

    indices_to_be_replaced = []
    # check if all hate len > 3 and target len < threshold, 
    for hate_profession in hate_professions:
        if occupation_len[hate_profession] > 3:
            num_to_be_replaced = occupation_len[hate_profession] - 3
            indices_to_be_replaced.extend(actual_idx[hate_profession][:num_to_be_replaced])

    for profession in ['士', '農', '工', '商', '俠']:
        if profession not in hate_professions and profession not in target_professions:
            if occupation_len[profession] > 4:
                num_to_be_replaced = occupation_len[profession] - 4
                indices_to_be_replaced.extend(actual_idx[profession][:num_to_be_replaced])
    
    messages = []
    
    for target_profession in target_professions:
        if occupation_len[target_profession] < threshold:
            num_to_be_added = threshold - occupation_len[target_profession]
            for idx in indices_to_be_replaced:
                messages.append(f'把 {buildings_list[idx]} 換成 {target_profession} 美女')
    
    if len(messages) == 0:
        messages.append('不用作任何的更改')
        
    st.session_state.user_input = {
        'messages': messages,
    }
    
    return messages

col1, col2, col3 = st.columns(3)
with col1:
    for index, row in enumerate(buildings_list):
        all_girls = [girl for values in girl_dict.values() for girl in values]
        unique_key_girl = f'select_girl_{buildings_list[index]}'
        
        # Ensure the default value is present in the list
        default_value = df.at[index, '美女']
        if default_value not in all_girls:
            all_girls.append(default_value)

        selected_girl = st.selectbox(f'入住{buildings_list[index]}的美女', all_girls, key=unique_key_girl, index=all_girls.index(default_value))
        df.at[index, '美女'] = selected_girl
        
        profession = get_key_by_value(girl_dict, selected_girl)
        df.at[index, '職業'] = profession
        
with col2:
    for index, row in enumerate(buildings_list):
        unique_key_quantity = f'input_quantity_{buildings_list[index]}'
        input_quantity = st.number_input(f'Enter quantity for {buildings_list[index]}', min_value=0, value=df.at[index, '應援物數量'], step=1, key=unique_key_quantity)
        df.at[index, '應援物數量'] = input_quantity
        
with col3:   
    target_professions = st.multiselect(f'缺少應援物的職業', ['士', '農', '工', '商', '俠'])
    hate_professions = st.multiselect(f'過多應援物的職業', ['士', '農', '工', '商', '俠'])
    
    tool_nums = list(df['應援物數量'].unique())
    
    st.session_state.user_input = {
        'df': df,
        'target_professions': target_professions,
        'hate_professions': hate_professions
    }
    
    cal_music_workshop_result = cal_music_workshop(df)
    # Display the total sums
    for profession, total_sum in cal_music_workshop_result.items():
        st.write(f'{profession}：{total_sum}')
    
    messages = make_suggestion(df)
    if '不用作任何的更改' in messages:
        st.success('不用作任何的更改')
    else:
        for msg in messages:
            st.error(msg)
    pass
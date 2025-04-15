import streamlit as st
import pandas as pd
from narratoAPI import NaAPI
import json 


# 设置全宽布局
st.set_page_config(layout="wide")

# 初始化API和session状态
if 'api' not in st.session_state:
    st.session_state.api = None
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# 顶部API密钥输入区
st.title("AI短剧解说")
with st.expander("API密钥设置", expanded=not st.session_state.api_key):

    with st.form("api_key_form"):
        api_key = st.text_input("API密钥", type="password", value=st.session_state.api_key)
        if st.form_submit_button("保存密钥"):
            st.session_state.api_key = api_key
            st.session_state.api = NaAPI(api_key=api_key)
            st.rerun()

# 密钥验证
if not st.session_state.api_key:
    st.error("请先输入并保存API密钥")
    st.stop()

# 顶部标签页导航
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "任务列表", "任务详情", "素材列表", "素材详情", "剪辑参数", "创建任务"
])

# 任务列表查询
with tab1:
    st.header("任务列表查询")
    col1, col2 = st.columns(2)
    with col1:
        limit = st.number_input("每页数量", min_value=1, value=10)
        page = st.number_input("页码", min_value=1, value=1)
    with col2:
        status = st.selectbox("状态筛选", [None, "0", "9"])
    
    if st.button("查询任务列表"):
        result = st.session_state.api.get_task_list(
            limit=limit, page=page, status=status
        )
        st.session_state.results['task_list'] = result
    if 'task_list' in st.session_state.results:
        st.dataframe(
            st.session_state.results['task_list'],
            use_container_width=True,
            hide_index=True,
            column_config={col: st.column_config.Column(width="small") for col in st.session_state.results['task_list'].columns}
        )
# 任务详情查询        
with tab2:
    st.header("任务详情查询")
    task_num = st.text_input("输入任务编号(多个编号用逗号或空格分隔)")
    if st.button("查询任务详情"):
        # 分割任务编号
        task_nums = [num.strip() for num in task_num.replace(',', ' ').split() if num.strip()]
        
        if not task_nums:
            st.warning("请输入至少一个任务编号")
        else:
            results = []
            progress_bar = st.progress(0)
            for i, num in enumerate(task_nums):
                try:
                    result = st.session_state.api.get_single_task_detail(num)
                    results.append(result)
                except Exception as e:
                    st.error(f"查询任务 {num} 失败: {str(e)}")
                progress_bar.progress((i + 1) / len(task_nums))
            
            if results:
                st.session_state.results['task_detail'] = results
                st.success(f"成功查询 {len(results)}/{len(task_nums)} 个任务")
    
    if 'task_detail' in st.session_state.results:
        # 处理单个或多个任务结果
        task_details = st.session_state.results['task_detail']
        if isinstance(task_details, list):
            # 多个任务结果合并
            dfs = [pd.json_normalize(detail) for detail in task_details]
            df = pd.concat(dfs, ignore_index=True)
        else:
            # 单个任务结果
            df = pd.json_normalize(task_details)
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                **{col: st.column_config.Column(width="small") for col in df.columns},
                "data.video_url": st.column_config.LinkColumn(
                    "视频链接",
                    display_text="视频文件",
                    width="small"  # 确保链接列也是小宽度
                ),
                "data.project_zip": st.column_config.LinkColumn(
                    "工程文件",
                    display_text="工程文件",
                    width="small"  # 确保链接列也是小宽度
                )
            }
        )

# 素材列表查询        
with tab3:
    st.header("素材列表查询")
    col1, col2 = st.columns(2)
    with col1:
        mat_limit = st.number_input("素材每页数量", min_value=1, value=10)
        mat_page = st.number_input("素材页码", min_value=1, value=1)
        
    with col2:
        mat_name=st.text_input("素材名称")
    
    if st.button("查询素材列表"):
        result = st.session_state.api.get_materials(
            limit=mat_limit, page=mat_page, name=mat_name
        )
        # 提取models字段中的name值合并成新数组
        if not result.empty and 'models' in result.columns:
            result['models'] = result['models'].apply(
                lambda x: ', '.join([m['name'] for m in x]) if isinstance(x, list) else x
            )
            
        st.session_state.results['material_list'] = result
        
    if 'material_list' in st.session_state.results:
        st.dataframe(
            st.session_state.results['material_list'],
            use_container_width=True,
            hide_index=True,
            column_config={col: st.column_config.Column(width="small") for col in st.session_state.results['material_list'].columns}
        )
# 素材详情查询
with tab4:
    st.header("素材详情查询")
    video_id = st.text_input("输入视频ID")
    if st.button("查询素材详情"):
        result = st.session_state.api.get_single_materials_detail(video_id)
        st.session_state.results['material_detail'] = result
        
    if 'material_detail' in st.session_state.results:
        df = pd.json_normalize(st.session_state.results['material_detail']['data'])
        df['models']=df['models'].apply(lambda x: ', '.join([m['name'] for m in x]) if isinstance(x, list) else x)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={col: st.column_config.Column(width="small") for col in df.columns}
        )  
        
# 剪辑参数查询
with tab5:
    st.header("剪辑参数")
    if st.button("查询剪辑参数"):
        try:
            result = st.session_state.api.get_options()
            st.session_state.results['edit_params'] = result['ai_model_v4']
            # 保存剪辑参数到JSON文件
            with open('edit_params.json', 'w') as f:
                json.dump(result['ai_model_v4'], f, ensure_ascii=False, indent=2)
            st.success("查询成功并已保存参数！")
        except Exception as e:
            st.error(f"查询失败: {str(e)}")
    
    if 'edit_params' in st.session_state.results:
        st.json(st.session_state.results['edit_params'])
# 创建任务
with tab6:
    st.header("创建新任务")
    
    # 添加重置按钮
    if st.button("重置表单"):
        if 'new_task' in st.session_state.results:
            del st.session_state.results['new_task']
        st.rerun()
    
    # 获取素材名称列表
    material_names = []
    if 'material_list' in st.session_state.results and not st.session_state.results['material_list'].empty:
        material_names = st.session_state.results['material_list']['name'].dropna().unique().tolist()
    
    # 尝试从保存的JSON文件中读取剪辑参数
    try:
        with open('edit_params.json', 'r') as f:
            edit_params = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        edit_params = None
    
    with st.form("create_task_form"):
        # 剧名选择下拉框
        if material_names:
            title = st.selectbox("剧名", material_names)
        else:
            st.warning("暂无可用素材名称，请先查询素材列表")
            title = st.text_input("剧名")
            
        model = st.selectbox("模型", ["六脉神剑", "其他模型"])
        dubbing = st.selectbox("配音", [f"{i['name']}" for i in edit_params['dubbing']] if edit_params else ["悦琳", "其他配音"])
        subtitle_style = st.selectbox("字幕样式", [i['name'] for i in edit_params['subtitle_style'] ]if edit_params else ["标准字幕"])
        cover = st.selectbox("封面样式", [i['name'] for i in edit_params['cover']] if edit_params else ["复古边框封面"])
        bgm = st.selectbox("背景音乐", [f"{i['name']}" for i in edit_params['bgm'] ] if edit_params else ["Happy-Is-A-State-of-Mind.wav.mp3"])
        video_type=st.selectbox("目标视频类型",[None,'short','long'])
        
        submitted = st.form_submit_button("提交创建")
        if submitted:
            result = st.session_state.api.create_task(
                title=title,
                model=model,
                dubbing=dubbing,
                # subtitle_style=subtitle_style,
                cover=cover,
                bgm=bgm,
                video_type=video_type
            )
            st.session_state.results['new_task'] = result
    if 'new_task' in st.session_state.results:
        st.success("任务创建成功！")
        st.json(st.session_state.results['new_task'])
        
        
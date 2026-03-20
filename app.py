import streamlit as st
import pandas as pd
import os
from datetime import date, datetime

# ==========================================
# --- 系统配置与初始化 ---
# ==========================================
st.set_page_config(page_title="中佳生物研发部物料管理", layout="wide")

# 定义数据文件路径（将自动生成在代码同级目录）
INV_FILE = "master_inventory.csv"
INBOUND_FILE = "inbound_log.csv"
OUTBOUND_FILE = "outbound_log.csv"

# 初始化数据文件
def init_files():
    if not os.path.exists(INV_FILE):
        df_inv = pd.DataFrame(columns=[
            "项目分类", "物品名称", "品牌及货号", "当前库存数量", "警戒阈值", "存放地址", "最近更新时间"
        ])
        df_inv.to_csv(INV_FILE, index=False)
        
    if not os.path.exists(INBOUND_FILE):
        df_in = pd.DataFrame(columns=[
            "入库单号", "项目分类", "物品名称", "品牌及货号", "入库数量", "存放地址", "入库日期", "登记人"
        ])
        df_in.to_csv(INBOUND_FILE, index=False)
        
    if not os.path.exists(OUTBOUND_FILE):
        df_out = pd.DataFrame(columns=[
            "出库单号", "项目分类", "物品名称", "品牌及货号", "领取数量", "出库日期", "领取人", "备注"
        ])
        df_out.to_csv(OUTBOUND_FILE, index=False)

init_files()

# 读取数据
def load_data(filename):
    df = pd.read_csv(filename, encoding='utf-8-sig')
    
    # 核心修复：将所有的空值(NaN)替换为空字符串
    df = df.fillna("") 
    
    # 防御性编程：强制把不是数量的列都转成纯文本类型
    for col in df.columns:
        if col not in ["当前库存数量", "警戒阈值", "入库数量", "领取数量"]:
            df[col] = df[col].astype(str)
            
    return df

# 保存数据
def save_data(df, filename):
    df.to_csv(filename, index=False)

# ==========================================
# --- 用户鉴权模块 ---
# ==========================================
# 1个管理员账号，3个研发人员账号
USERS = {
    "admin": {"password": "123", "role": "管理员", "name": "管理员"},
    "rd1": {"password": "123", "role": "研发人员", "name": "研发人员A"},
    "rd2": {"password": "123", "role": "研发人员", "name": "研发人员B"},
    "rd3": {"password": "123", "role": "研发人员", "name": "研发人员C"}
}

def login_page():
    # 注入CSS美化登录界面
    st.markdown("""
        <style>
        /* 1. 设置全屏背景为图片 */
        .stApp {
            background-image: url("https://hporhdgbqajajdbefynt.supabase.co/storage/v1/object/public/Zhongjia/56211398.png");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        
        /* 🔥 将顶部的 Streamlit 默认页眉背景设为透明，解决顶部不覆盖问题 🔥 */
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }

        /* 2. 标题美化：居中，正蓝色字体，强制同行，浅色立体阴影衬托 */
        .login-title {
            color: #0000FF !important; 
            text-align: center;
            font-size: 2.8rem;
            font-weight: bold;
            margin-bottom: 30px;
            margin-top: 15px;
            white-space: nowrap; 
            text-shadow: 1px 1px 3px rgba(255, 255, 255, 0.8); 
        }
        
        /* 3. 用户名和密码标签左对齐并加粗 */
        .stTextInput label {
            display: flex;
            justify-content: flex-start; 
            font-size: 1.1rem;
            color: #333; 
            font-weight: bold;
        }
        
        /* 4. 登录框（表单）美化：50%透明背景、毛玻璃效果、圆角、明显黑色悬浮阴影 */
        /* 修改：限制最大宽度为 600px 并水平居中 */
        [data-testid="stForm"] {
            background-color: rgba(255, 255, 255, 0.5) !important; 
            backdrop-filter: blur(8px); /* 毛玻璃模糊滤镜 */
            -webkit-backdrop-filter: blur(8px); /* 兼容苹果 Safari */
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0px 15px 35px rgba(0, 0, 0, 0.6); /* 保持明显的黑色悬浮阴影 */
            border: 1px solid rgba(255, 255, 255, 0.4); /* 增强玻璃质感的淡白边 */
            max-width: 600px; /* 限制最大宽度 */
            margin-left: auto; /* 水平居中 */
            margin-right: auto; /* 水平居中 */
        }
        
        /* 🔥 5. 新增：按钮立体美化 & 颜色协调（蓝宝石色渐变） 🔥 */
        div[data-testid="stFormSubmitButton"] > button {
            /* 协调色：深蓝色渐变 */
            background-image: linear-gradient(180deg, #1E88E5 0%, #1565C0 100%) !important;
            color: white !important;
            
            /* 立体感边框：顶部浅、底部深 */
            border: 1px solid #0D47A1 !important;
            border-top: 1px solid #64B5F6 !important;
            border-radius: 12px !important; /* 圆角配合登录框 */
            
            font-weight: bold !important;
            font-size: 1.1rem !important;
            padding: 10px 24px !important;
            
            /* 🔥 核心立体阴影：Y轴下移 5px 的暗蓝色阴影营造厚度 🔥 */
            box-shadow: 0 5px 0 #0D47A1, 0 8px 15px rgba(0, 0, 0, 0.3) !important;
            
            /* 丝滑过渡反馈 */
            transition: all 0.1s ease !important;
            cursor: pointer !important;
        }
        
        /* 按钮鼠标悬停反馈：稍微变亮 */
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-image: linear-gradient(180deg, #42A5F5 0%, #1976D2 100%) !important;
        }
        
        /* 🔥 按钮点击/按下反馈：核心立体下沉效果 🔥 */
        div[data-testid="stFormSubmitButton"] > button:active {
            /* 缩短阴影营造被按下的视觉 */
            box-shadow: 0 2px 0 #0D47A1, 0 4px 6px rgba(0, 0, 0, 0.3) !important;
            /* 按钮整体垂直下移，模拟物理下沉 */
            transform: translateY(3px) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # === 第一部分：Logo与标题 ===
    # 给标题分配更宽的空间（比例 1:4:1），彻底摆脱登录框的宽度限制
    header_col1, header_col2, header_col3 = st.columns([1, 4, 1])
    with header_col2:
        logo_url = "https://hporhdgbqajajdbefynt.supabase.co/storage/v1/object/public/Zhongjia/28827220.png"
        # 使用 HTML 统一渲染图片和标题，确保绝对居中且不换行
        # 修改：Logo 图片宽度增大 2 倍（160px -> 320px），标题更新，Logo 与标题间距增加
        # 修改：标题与登录框直接增加 48px 的间隔 (通过 login-title 的 margin-bottom 或整体容器的 margin-bottom 实现)
        st.markdown(f"""
            <div style="text-align: center; margin-top: 2rem; margin-bottom: 48px;"> <img src="{logo_url}" width="320" style="margin-bottom: 20px; drop-shadow(0px 4px 6px rgba(0,0,0,0.2));" /> <div class='login-title'>实验试剂与耗材使用管理系统</div> </div>
        """, unsafe_allow_html=True)

    # === 第二部分：半透明高对比度登录框 ===
    # 保持登录框宽度适中且居中（比例 1:1.2:1）
    # 修改：不需要 col columns，CSS 已经处理了 max-width 和 centering
    # col1, col2, col3 = st.columns([1, 1.2, 1])
    # with col2:
    with st.form("login_form"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        
        st.write("") # 留出少许间距
        
        # 使用列布局使“登录”按钮完美居中
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1.2, 1])
        with btn_col2:
            # use_container_width=True 让按钮铺满这一列
            submit = st.form_submit_button("登录系统", use_container_width=True)
        
        if submit:
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user_info = USERS[username]
                st.success(f"登录成功！欢迎，{USERS[username]['name']}")
                st.rerun()
            else:
                st.error("用户名或密码错误！")

# ==========================================
# --- 模块1：采购登记入库 ---
# ==========================================
def inbound_module():
    st.header("📥 模块一：采购登记入库")
    
    inv_df = load_data(INV_FILE)
    inbound_df = load_data(INBOUND_FILE)
    
    with st.form("inbound_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("项目分类", ["试剂", "耗材", "设备"])
            item_name = st.text_input("物品名称", placeholder="例如：无水乙醇、10ml离心管...")
            brand_cat = st.text_input("品牌及货号", placeholder="例如：Sigma 12345")
            quantity = st.number_input("入库数量 (规格数量)", min_value=0.0, step=1.0)
        with col2:
            location = st.text_input("存放地址", placeholder="例如：4度冰箱2层、试剂柜A...")
            inbound_date = st.date_input("入库日期", value=date.today())
            registrant = st.text_input("登记人", value=st.session_state.user_info['name'])
            threshold = st.number_input("设置余量警戒限 (低于此值将报警)", min_value=1.0, value=10.0, step=1.0)
            
        submitted = st.form_submit_button("📝 确认登记入库")
        
        if submitted:
            if not item_name or not brand_cat:
                st.warning("⚠️ 物品名称和品牌货号不能为空！")
            else:
                new_inbound = {
                    "入库单号": f"IN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "项目分类": category,
                    "物品名称": item_name,
                    "品牌及货号": brand_cat,
                    "入库数量": quantity,
                    "存放地址": location,
                    "入库日期": inbound_date.strftime("%Y-%m-%d"),
                    "登记人": registrant
                }
                inbound_df = pd.concat([inbound_df, pd.DataFrame([new_inbound])], ignore_index=True)
                save_data(inbound_df, INBOUND_FILE)
                
                mask = (inv_df["物品名称"] == item_name) & (inv_df["品牌及货号"] == brand_cat)
                if inv_df[mask].empty:
                    new_inv = {
                        "项目分类": category,
                        "物品名称": item_name,
                        "品牌及货号": brand_cat,
                        "当前库存数量": quantity,
                        "警戒阈值": threshold,
                        "存放地址": location,
                        "最近更新时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    inv_df = pd.concat([inv_df, pd.DataFrame([new_inv])], ignore_index=True)
                else:
                    idx = inv_df[mask].index[0]
                    inv_df.at[idx, "当前库存数量"] += quantity
                    inv_df.at[idx, "存放地址"] = location
                    inv_df.at[idx, "警戒阈值"] = threshold
                    inv_df.at[idx, "最近更新时间"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                save_data(inv_df, INV_FILE)
                st.success(f"✅ 【{item_name}】 入库登记成功！总库存已同步更新。")

# ==========================================
# --- 模块2：领取出库登记 ---
# ==========================================
def outbound_module():
    st.header("📤 模块二：领取出库登记")
    
    inv_df = load_data(INV_FILE)
    outbound_df = load_data(OUTBOUND_FILE)
    
    if inv_df.empty:
        st.info("当前库存为空，无法进行出库操作。请先进入模块一进行入库。")
        return
        
    inv_df["显示名称"] = inv_df["项目分类"] + " - " + inv_df["物品名称"] + " (" + inv_df["品牌及货号"] + ")" + " | 当前余量: " + inv_df["当前库存数量"].astype(str)
    item_options = inv_df["显示名称"].tolist()
    
    with st.form("outbound_form", clear_on_submit=True):
        selected_item = st.selectbox("选择要领取的物品 (项目分类 - 名称 - 品牌货号 | 余量)", ["请选择..."] + item_options)
        withdraw_qty = st.number_input("领取规格数量", min_value=0.1, step=1.0)
        receiver = st.text_input("领取人", value=st.session_state.user_info['name'])
        notes = st.text_input("备注 (如：用于某某实验项目)")
        
        submitted = st.form_submit_button("📦 确认领取出库")
        
        if submitted:
            if selected_item == "请选择...":
                st.warning("⚠️ 请先选择要领取的物品！")
            else:
                selected_idx = item_options.index(selected_item)
                target_row = inv_df.iloc[selected_idx]
                current_qty = target_row["当前库存数量"]
                
                if withdraw_qty > current_qty:
                    st.error(f"❌ 库存不足！当前仅剩余 {current_qty}，无法领取 {withdraw_qty}。")
                else:
                    new_outbound = {
                        "出库单号": f"OUT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "项目分类": target_row["项目分类"],
                        "物品名称": target_row["物品名称"],
                        "品牌及货号": target_row["品牌及货号"],
                        "领取数量": withdraw_qty,
                        "出库日期": date.today().strftime("%Y-%m-%d"),
                        "领取人": receiver,
                        "备注": notes
                    }
                    outbound_df = pd.concat([outbound_df, pd.DataFrame([new_outbound])], ignore_index=True)
                    save_data(outbound_df, OUTBOUND_FILE)
                    
                    inv_df.at[selected_idx, "当前库存数量"] -= withdraw_qty
                    inv_df.at[selected_idx, "最近更新时间"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    save_inv_df = inv_df.drop(columns=["显示名称"])
                    save_data(save_inv_df, INV_FILE)
                    
                    st.success(f"✅ 【{target_row['物品名称']}】 领取出库登记成功！")

# ==========================================
# --- 模块3：数量不足提醒和总量清单 ---
# ==========================================
def inventory_and_alert_module():
    st.header("📊 模块三：数量不足提醒和总量清单")
    
    inv_df = load_data(INV_FILE)
    
    if not inv_df.empty:
        alert_df = inv_df[inv_df["当前库存数量"] <= inv_df["警戒阈值"]]
        if not alert_df.empty:
            st.error("🚨 **库存告警公告板 (以下物资即将耗尽，请尽快采购！)**")
            for index, row in alert_df.iterrows():
                st.warning(f"🔺 **{row['物品名称']}** ({row['品牌及货号']}) - 当前仅剩: **{row['当前库存数量']}** (警戒线: {row['警戒阈值']})，存放于: {row['存放地址']}")
        else:
            st.success("✨ 当前所有试剂耗材库存充足，未触发警戒线。")
    
    st.divider()
    
    st.subheader("📦 当前试剂耗材库存总量清单")
    st.markdown("您可以直接在此表格中快速修改**警戒阈值**或**存放地址**（修改后点击保存）。总数量与出入库自动关联。")
    
    if not inv_df.empty:
        edited_df = st.data_editor(
            inv_df,
            column_config={
                "项目分类": st.column_config.TextColumn("项目分类", disabled=True),
                "物品名称": st.column_config.TextColumn("物品名称", disabled=True),
                "品牌及货号": st.column_config.TextColumn("品牌及货号", disabled=True),
                "当前库存数量": st.column_config.NumberColumn("当前库存数量 (联动)", disabled=True),
                "警戒阈值": st.column_config.NumberColumn("警戒阈值 (可修改)"),
                "存放地址": st.column_config.TextColumn("存放地址 (可修改)"),
                "最近更新时间": st.column_config.TextColumn("最近更新时间", disabled=True)
            },
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("💾 保存对清单的修改"):
            save_data(edited_df, INV_FILE)
            st.success("清单信息已更新！")
            st.rerun()
            
        csv = edited_df.to_csv(index=False).encode('utf-8-sig') 
        st.download_button(
            label="⬇️ 下载库存总清单 (CSV格式，可用Excel打开)",
            data=csv,
            file_name=f'中佳生物_库存清单_{date.today()}.csv',
            mime='text/csv',
        )
        
        st.divider()
        st.subheader("⬆️ 上传初始化/覆盖库存清单")
        st.markdown("⚠️ **注意**：上传的CSV文件表头必须包含：`项目分类,物品名称,品牌及货号,当前库存数量,警戒阈值,存放地址,最近更新时间`。上传将**直接覆盖**现有总库存！")
        uploaded_file = st.file_uploader("选择CSV文件", type=['csv'])
        if uploaded_file is not None:
            if st.button("确认覆盖导入"):
                try:
                    upload_df = pd.read_csv(uploaded_file)
                    save_data(upload_df, INV_FILE)
                    st.success("✅ 导入成功！界面将自动刷新。")
                    st.rerun()
                except Exception as e:
                    st.error(f"导入失败，请检查文件格式是否正确。错误信息：{e}")
    else:
        st.info("当前总库存为空，暂无数据展示。")

# ==========================================
# --- 应用程序主控制流 ---
# ==========================================
if __name__ == "__main__":
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
    else:
        st.sidebar.title("中佳生物系统菜单")
        st.sidebar.markdown(f"**操作员:** {st.session_state.user_info['name']} ({st.session_state.user_info['role']})")
        
        menu = st.sidebar.radio(
            "选择系统模块",
            ["模块一：采购登记入库", "模块二：领取出库登记", "模块三：库存清单与提醒"]
        )
        
        st.sidebar.divider()
        if st.sidebar.button("🚪 退出登录"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_info = None
            st.rerun()
            
        if menu == "模块一：采购登记入库":
            inbound_module()
        elif menu == "模块二：领取出库登记":
            outbound_module()
        elif menu == "模块三：库存清单与提醒":
            inventory_and_alert_module()

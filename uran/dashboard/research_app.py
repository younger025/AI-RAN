import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import time
import streamlit as st
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from uran.dashboard.research_controller import ResearchDemoController
from uran.dashboard.topology_view import draw_topology
from uran.dashboard.kpi_charts import (
    plot_snr_sinr_curve,
    plot_bler_curve,
    plot_throughput_curve,
    plot_latency_curve,
    plot_adaptation_params,
    plot_reliability_curve,
)
from uran.dashboard.timeline_view import build_event_timeline, render_event_timeline
from uran.dashboard.report_exporter import (
    ensure_output_dirs,
    timestamp_str,
    export_kpi_csv,
    export_kpi_json,
    export_plotly_html,
    generate_experiment_summary,
    export_markdown_summary,
)

from uran.ai.orchestrator import AIOrchestrator
from uran.ai.intent_schema import EnvironmentSpec
from uran.twin.sandbox import DigitalTwinSandbox
from uran.twin.report import TwinValidationReport
from uran.modules.registry import build_default_registry
from uran.runtime.microkernel import MicrokernelRuntime
from uran.sdr.mock_sdr import MockSDRAdapter
from uran.evolution.evolution_loop import EvolutionLoop
from uran.evolution.data_lake import DataLake
from uran.demo.end_to_end import run_end_to_end_demo
from uran.common.band_config import BandConfig, BAND_PRESETS, build_custom_band, get_band_config

SCENARIO_FILES = {
    "点对点链路自适应": "p2p_link_adaptation.yaml",
    "多节点RAN微型小区": "multi_node_cell.yaml",
    "干扰与自演进": "jamming_self_evolution.yaml",
    "遮挡与恢复": "blockage_recovery.yaml",
}

PAGES = [
    "系统首页",
    "系统核心算法介绍",
    "模块1: 链路自适应仿真与KPI可视化",
    "模块2: AI意图解析与方案生成",
    "模块3: 数字孪生方案验证",
    "模块4: 微内核Runtime运行监控",
    "模块5: Mock SDR半实物演示",
    "模块6: 自演进闭环优化",
    "端到端：全流程一键演示",
]


def get_current_band_config():
    controller: ResearchDemoController = st.session_state.research_controller
    return controller.band_config


def init_session_state():
    defaults = {
        "research_controller": ResearchDemoController(band_config=BAND_PRESETS["n41_100mhz"]),
        "auto_run": False,
        "ai_result": None,
        "twin_reports": None,
        "twin_plan": None,
        "runtime_result": None,
        "sdr_metrics": None,
        "evolution_result": None,
        "end_to_end_result": None,
        "band_key": "n41_100mhz",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def page_home():
    st.markdown("""
    <style>
    .home-container {
        max-width: 1100px;
        margin: 0 auto;
    }
    .home-hero-title {
        margin-bottom: 20px;
    }
    .home-hero-title .line1 {
        font-size: 38px;
        font-weight: 800;
        color: #1e40af;
        line-height: 1.2;
        letter-spacing: -0.5px;
    }
    .home-hero-title .line2 {
        font-size: 15px;
        font-weight: 500;
        color: #60a5fa;
        margin-top: 6px;
        letter-spacing: 0.3px;
    }
    .home-slogan {
        font-size: 17px;
        color: #475569;
        line-height: 1.7;
        padding: 14px 18px;
        border-left: 3px solid #3b82f6;
        background: #f8fafc;
        border-radius: 6px;
        margin: 16px 0 20px;
    }
    .home-subtitle {
        font-size: 15px;
        color: #64748b;
        margin-bottom: 28px;
        line-height: 1.6;
    }
    .home-section-title {
        font-size: 20px;
        font-weight: 700;
        color: #334155;
        margin-bottom: 4px;
    }
    .home-section-desc {
        font-size: 13px;
        color: #94a3b8;
        margin-bottom: 16px;
    }
    .home-card {
        border: 1px solid #e2e8f0;
        background: #ffffff;
        border-radius: 10px;
        padding: 20px 18px;
        height: 100%;
    }
    .home-card .card-label {
        font-size: 11px;
        color: #3b82f6;
        font-weight: 600;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }
    .home-card .card-title {
        font-size: 17px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
    }
    .home-card .card-desc {
        font-size: 13px;
        color: #64748b;
        line-height: 1.65;
        margin: 0;
    }
    .home-cap-icon {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-bottom: 12px;
    }
    .home-footer {
        text-align: center;
        padding: 28px 20px;
        margin-top: 36px;
        border-top: 1px solid #e2e8f0;
    }
    .home-footer p {
        font-size: 14px;
        color: #94a3b8;
        margin: 0;
    }
    hr.home-divider {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 28px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="home-container">', unsafe_allow_html=True)

    st.markdown("""
    <div class="home-hero-title">
        <div class="line1">基于微内核的自演进 RAN 原型</div>
        <div class="line2">Microkernel-based Self-Evolving RAN Prototype</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="home-slogan">
        让无线网络像智能体一样，理解任务、设计方案、验证风险、执行策略，并在运行中持续进化。
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="home-subtitle">'
        '本系统面向未来 6G/7G 智能无线网络，围绕 AI-Native RAN (Microkernel-based Self-Evolving RAN Prototype) 关键科学问题，'
        '构建基于通信微内核的自设计、自验证、自运行、自演进原型平台。'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="home-divider">', unsafe_allow_html=True)

    st.markdown('<div class="home-section-title">系统核心关键词</div>', unsafe_allow_html=True)
    st.markdown('<div class="home-section-desc">以通信微内核为底座，以 AI 自设计为核心，以网络自演进为目标</div>', unsafe_allow_html=True)

    keywords = [
        ("通信微内核",
         "将调制、编码、调度、重传、功控等能力拆解为可注册、可组合、可替换的模块，由微内核统一调度运行。"),
        ("AI 自设计",
         "AI 根据任务意图、环境状态和性能目标自动生成通信策略，实现面向场景的自主方案设计。"),
        ("网络自演进",
         "通过运行反馈、经验记忆和策略优化，持续积累场景知识，实现从单次优化到持续演进的能力跃迁。"),
    ]
    kw_cols = st.columns(3)
    for i, (title, desc) in enumerate(keywords):
        with kw_cols[i]:
            st.markdown(f"""
            <div class="home-card">
                <div class="card-label">0{i+1}</div>
                <div class="card-title">{title}</div>
                <p class="card-desc">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<hr class="home-divider">', unsafe_allow_html=True)

    st.markdown('<div class="home-section-title">核心功能能力</div>', unsafe_allow_html=True)
    st.markdown('<div class="home-section-desc">从任务输入、AI 方案生成、数字孪生验证到反馈学习的端到端闭环</div>', unsafe_allow_html=True)

    capabilities = [
        ("🎯", "任务意图理解", "支持自然语言或结构化方式输入通信任务，自动识别业务目标、场景约束和关键性能指标。"),
        ("⚡", "AI 通信方案生成", "基于 AI Planner 自动生成调制、编码、调度、功控、重传等通信策略组合。"),
        ("🛡️", "数字孪生验证", "在部署前通过数字孪生沙箱评估方案性能、风险边界和可行性。"),
        ("🔄", "反馈学习演进", "采集运行 KPI，形成经验记忆，反向驱动策略优化，实现持续学习演进。"),
    ]
    cap_cols = st.columns(4)
    for icon, title, desc in capabilities:
        with cap_cols[capabilities.index((icon, title, desc))]:
            st.markdown(f"""
            <div class="home-card">
                <div class="home-cap-icon">{icon}</div>
                <div class="card-title">{title}</div>
                <p class="card-desc">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class="home-footer">
        <p>AI-Native RAN (Microkernel-based Self-Evolving RAN Prototype) · 通过左侧导航栏进入各功能模块</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-top:10px;padding:14px 20px;background:linear-gradient(135deg,#eff6ff,#dbeafe);border:1px solid #bfdbfe;border-radius:10px;">
        <span style="font-size:15px;">📖</span>
        <span style="font-size:13px;color:#1e40af;font-weight:600;margin-left:4px;">想了解系统内部算法的实现原理？</span>
        <span style="font-size:12px;color:#64748b;margin-left:6px;">在左侧导航栏选择「<strong>系统核心算法介绍</strong>」，查看 26 个核心算法的功能、实现思路与公式推导。</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def page_phase1_simulation():
    st.title("AI-Native RAN (Microkernel-based Self-Evolving RAN Prototype): 链路自适应可视化")
    st.caption("链路自适应、KPI 演进与科研汇报的通信可视化平台。")
    ensure_output_dirs()
    controller: ResearchDemoController = st.session_state.research_controller

    with st.container():
        col_sc, col_a, col_b, col_c, col_d, col_ar, col_ai = st.columns([2.2, 1, 1, 1, 1, 1, 1.5])
        with col_sc:
            scenario_name = st.selectbox("场景", list(SCENARIO_FILES.keys()), label_visibility="collapsed")
            scenario_file = SCENARIO_FILES[scenario_name]
        with col_a:
            init_clicked = st.button("初始化", use_container_width=True)
        with col_b:
            reset_clicked = st.button("重置", use_container_width=True)
        with col_c:
            step_clicked = st.button("单步", use_container_width=True)
        with col_d:
            run_all_clicked = st.button("全部", use_container_width=True)
        with col_ar:
            auto_run = st.checkbox("自动", value=st.session_state.auto_run)
            st.session_state.auto_run = auto_run
        with col_ai:
            animation_interval = st.slider("间隔(秒)", 0.05, 1.0, 0.2, 0.05, label_visibility="collapsed")

    st.divider()

    if init_clicked:
        controller.load_scenario(scenario_file)
        st.success(f"场景已初始化: {scenario_name}")
    if reset_clicked:
        controller.reset()
        st.info("实验已重置。")

    if not controller.is_loaded():
        st.info("请在上方选择场景并点击「初始化」开始。")
        st.markdown("""
        ### 欢迎使用 AI-Native RAN 科研演示平台

        本平台展示面向下一代无线通信的 **AI 驱动链路自适应** 技术。

        **核心功能:**
        - 多节点网络拓扑可视化（基站、终端、干扰源）
        - 7 种时变信道模式
        - 实时自适应 MCS、调制、编码、HARQ 与功率控制
        - 实时 KPI 监控：SNR、SINR、BLER、吞吐量、时延、频谱效率
        - 事件时间线记录所有自适应决策
        - 支持论文与演示导出（CSV、JSON、HTML、Markdown）

        **快速开始:** 选择一个场景，点击 **初始化**。
        """)
        return

    if step_clicked:
        controller.step()
    if run_all_clicked:
        controller.run_all()
    if st.session_state.auto_run and not controller.is_finished():
        controller.step()
        time.sleep(animation_interval)
        st.rerun()

    topology = controller.topology()
    df = controller.dataframe()
    latest = controller.latest_records_by_link()
    current_step = controller.current_step()
    total_steps = controller.total_steps()

    st.subheader("实验进度")
    st.progress(min(1.0, current_step / max(total_steps, 1)))

    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
    with col_info1:
        st.metric("当前步数", f"{current_step} / {total_steps}")
    with col_info2:
        st.metric("已用时间", f"{current_step * 0.1:.1f}秒")
    with col_info3:
        st.metric("活跃链路", f"{len(topology.get_active_links())}")
    with col_info4:
        st.metric("状态", "运行中" if not controller.is_finished() else "已完成")

    st.subheader("网络拓扑")
    col_topo, col_legend = st.columns([4, 1])
    with col_topo:
        fig_topology = draw_topology(topology, latest)
        st.plotly_chart(fig_topology, width="stretch")
    with col_legend:
        st.markdown("**链路质量图例:**")
        st.markdown("🟢 BLER < 3% (良好)")
        st.markdown("🟠 3% <= BLER < 10% (警告)")
        st.markdown("🔴 BLER >= 10% (严重)")
        st.markdown("⬛ 暂无KPI数据")
        st.divider()
        st.markdown("**节点类型:**")
        st.markdown("🟦 gNB (基站)")
        st.markdown("🟢 UE (终端)")
        st.markdown("❌ Jammer (干扰源)")

    st.subheader("当前链路状态")
    if latest:
        st.dataframe([r.model_dump() for r in latest.values()], width="stretch")
    else:
        st.info("暂无KPI记录。请点击「单步执行」或「全部运行」。")

    if df is None or df.empty:
        return

    st.subheader("核心KPI曲线")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_snr_sinr_curve(df), width="stretch")
    with col2:
        st.plotly_chart(plot_bler_curve(df), width="stretch")

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(plot_throughput_curve(df), width="stretch")
    with col4:
        st.plotly_chart(plot_latency_curve(df), width="stretch")

    st.subheader("自适应通信参数")
    fig_params = plot_adaptation_params(df)
    st.plotly_chart(fig_params, width="stretch")

    st.subheader("可靠性")
    st.plotly_chart(plot_reliability_curve(df), width="stretch")

    st.subheader("事件时间线")
    render_event_timeline(build_event_timeline(df))

    st.subheader("论文与演示导出")
    export_col1, export_col2, export_col3, export_col4 = st.columns(4)
    ts = timestamp_str()
    scenario_id = controller.config.get("scenario_id", "scenario") if controller.config else "scenario"

    with export_col1:
        if st.button("导出 CSV", width="stretch"):
            path = export_kpi_csv(df, Path("outputs/experiment_logs") / f"{scenario_id}_{ts}.csv")
            st.success(f"CSV 已导出: {path}")
    with export_col2:
        if st.button("导出 JSON", width="stretch"):
            path = export_kpi_json(df, Path("outputs/experiment_logs") / f"{scenario_id}_{ts}.json")
            st.success(f"JSON 已导出: {path}")
    with export_col3:
        if st.button("导出 HTML 图表", width="stretch"):
            fig_snr = plot_snr_sinr_curve(df)
            fig_bler = plot_bler_curve(df)
            fig_thr = plot_throughput_curve(df)
            export_plotly_html(fig_snr, Path("outputs/figures") / f"{scenario_id}_snr_{ts}.html")
            export_plotly_html(fig_bler, Path("outputs/figures") / f"{scenario_id}_bler_{ts}.html")
            export_plotly_html(fig_thr, Path("outputs/figures") / f"{scenario_id}_throughput_{ts}.html")
            export_plotly_html(fig_params, Path("outputs/figures") / f"{scenario_id}_params_{ts}.html")
            st.success("HTML 图表已导出。")
    with export_col4:
        if st.button("导出摘要", width="stretch"):
            summary = generate_experiment_summary(df, scenario_name=scenario_name)
            path = export_markdown_summary(summary, Path("outputs/experiment_logs") / f"{scenario_id}_summary_{ts}.md")
            st.success(f"摘要已导出: {path}")

    with st.expander("Markdown 实验摘要预览"):
        st.markdown(generate_experiment_summary(df, scenario_name=scenario_name))


def page_ai_orchestration():
    st.title("模块2: AI意图解析与通信方案生成")
    st.caption("基于用户自然语言意图，AI多智能体协作生成候选通信方案。")

    raw_intent = st.text_area(
        "输入通信意图 (自然语言)",
        value="在 SNR 约为 8 dB 的高铁场景下，要求 BLER < 5%，吞吐量 > 500 kbps，时延 < 50 ms。",
        height=80,
    )

    col_env1, col_env2, col_env3, col_env4 = st.columns(4)
    with col_env1:
        snr_db = st.number_input("SNR (dB)", value=8.0, step=1.0)
    with col_env2:
        scenario = st.selectbox("场景", ["high_speed", "urban", "indoor", "rural", "jamming"])
    with col_env3:
        mobility = st.selectbox("移动性", ["low", "medium", "high"])
    with col_env4:
        channel_mode = st.selectbox("信道变化", ["constant", "sinusoidal", "blockage"])

    if st.button("生成方案", type="primary"):
        with st.spinner("AI多智能体正在编排..."):
            orchestrator = AIOrchestrator(seed=42)
            doppler_map = {"low": 5, "medium": 20, "high": 80}
            channel_map = {"constant": "awgn", "sinusoidal": "fading", "blockage": "rayleigh"}
            env = EnvironmentSpec(
                avg_snr_db=snr_db,
                avg_sinr_db=snr_db - 2,
                doppler_hz=doppler_map.get(mobility, 20),
                interference_level="medium",
                channel_type=channel_map.get(channel_mode, "rayleigh"),
                node_count=1,
                mobility_level=mobility,
                spectrum_congestion="medium",
            )
            result = orchestrator.generate_plan(raw_intent, environment=env)
            st.session_state.ai_result = result
        st.success("方案生成完成!")

    result = st.session_state.ai_result
    if result is None:
        st.info("请输入意图并点击「生成方案」开始。")
        return

    intent = result["intent"]
    env = result["environment"]
    plans = result["candidate_plans"]
    trace = result["trace"]

    st.subheader("解析后的意图")
    col_i1, col_i2, col_i3, col_i4 = st.columns(4)
    with col_i1:
        st.metric("目标BLER", f"{intent.target_bler:.2%}")
    with col_i2:
        st.metric("最小吞吐量", f"{intent.min_throughput_kbps} kbps")
    with col_i3:
        st.metric("最大时延", f"{intent.max_latency_ms} ms")
    with col_i4:
        st.metric("场景", intent.scenario_type)

    st.subheader("环境信息")
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    with col_e1:
        st.metric("SNR", f"{env.avg_snr_db} dB")
    with col_e2:
        st.metric("SINR", f"{env.avg_sinr_db} dB")
    with col_e3:
        st.metric("移动性", env.mobility_level)
    with col_e4:
        st.metric("信道类型", env.channel_type)

    st.subheader("AI编排执行轨迹")
    for step in trace:
        st.markdown(f"**{step['agent']}** → {step['message']}")

    st.subheader("候选通信方案")
    for i, plan in enumerate(plans):
        with st.expander(f"方案 {i + 1}: {plan.name} ({plan.modulation} / {plan.coding_scheme} R={plan.coding_rate:.2f})"):
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                st.markdown(f"**调制**: {plan.modulation}")
                st.markdown(f"**编码**: {plan.coding_scheme} (R={plan.coding_rate:.2f})")
                st.markdown(f"**MCS等级**: {plan.mcs}")
            with col_p2:
                st.markdown(f"**HARQ**: {'启用 (max_retx=' + str(plan.harq_max_retx) + ')' if plan.harq_enabled else '禁用'}")
                st.markdown(f"**导频密度**: {plan.pilot_density}")
                st.markdown(f"**功率控制**: {plan.power_control}")
            with col_p3:
                st.markdown(f"**调度器**: {plan.scheduler}")
                st.markdown(f"**发射功率**: {plan.tx_power_dbm} dBm")
                st.markdown(f"**风险等级**: {plan.risk_level}")

            st.markdown(f"**方案描述**: {plan.description}")


def page_digital_twin():
    st.title("模块3: 数字孪生方案验证")
    st.caption("在数字孪生沙箱中对候选方案进行接口检查、约束验证、链路仿真、故障注入和综合评分。")

    if st.button("从AI编排获取方案", type="primary"):
        with st.spinner("生成方案并验证..."):
            orchestrator = AIOrchestrator(seed=42)
            result = orchestrator.generate_plan(
                "在 SNR 约为 8 dB 的高铁场景下，要求 BLER < 5%，吞吐量 > 500 kbps，时延 < 50 ms。"
            )
            st.session_state.ai_result = result
            sandbox = DigitalTwinSandbox(band_config=get_current_band_config())
            reports = [
                sandbox.validate(p, result["intent"], result["environment"])
                for p in result["candidate_plans"]
            ]
            st.session_state.twin_reports = reports
            st.session_state.twin_plan = result["candidate_plans"][0]
        st.success("验证完成!")

    results = st.session_state.ai_result
    reports = st.session_state.twin_reports

    if results is None:
        st.info("请点击「从AI编排获取方案」开始验证。")
        return

    st.subheader("候选方案验证结果")
    for i, (plan, report) in enumerate(zip(results["candidate_plans"], reports)):
        icon = "✅" if report.decision == "ACCEPT" else "❌"
        with st.expander(f"{icon} 方案 {i + 1}: {plan.plan_id} (最终得分: {report.final_score:.1f})"):
            st.markdown(f"**决策**: {report.decision}")
            st.markdown(f"**评分理由**: {'方案可行，各项指标达标' if report.passed else '方案未通过验证，存在风险'}")

            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.markdown("**接口检查**")
                status_icon = "✅" if report.interface_check_passed else "❌"
                st.markdown(f"{status_icon} 接口兼容性检查")
                st.markdown(f"**约束验证**")
                fc_icon = "✅" if report.fallback_test_passed else "❌"
                st.markdown(f"{fc_icon} 回退安全测试")
            with col_r2:
                st.markdown("**链路仿真KPI**")
                st.metric("BLER", f"{report.bler:.4f}")
                st.metric("吞吐量", f"{report.throughput_kbps:.1f} kbps")
                st.metric("时延", f"{report.latency_ms:.1f} ms")
            with col_r3:
                st.markdown("**综合评分**")
                st.metric("频谱效率", f"{report.spectral_efficiency:.2f} bps/Hz")
                st.metric("能耗成本", f"{report.energy_cost:.2f}")
                st.metric("鲁棒性", f"{report.robustness_score:.1f}")

            if report.warnings:
                st.markdown("**告警**")
                for w in report.warnings:
                    st.markdown(f"⚠️ {w}")
            if report.suggestions:
                st.markdown("**建议**")
                for s in report.suggestions:
                    st.markdown(f"💡 {s}")


def page_runtime():
    st.title("模块4: 微内核Runtime运行监控")
    st.caption("加载通信方案到微内核Runtime，实时监控模块运行状态、KPI和安全回退。")

    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        if st.button("加载方案并运行50步", type="primary"):
            with st.spinner("Runtime运行中..."):
                orchestrator = AIOrchestrator(seed=42)
                result = orchestrator.generate_plan(
                    "在 SNR 约为 12 dB 的城市宏基站场景下，要求 BLER < 3%，吞吐量 > 800 kbps。"
                )
                registry = build_default_registry()
                runtime = MicrokernelRuntime(registry=registry, seed=42)
                best_plan = result["candidate_plans"][0]
                runtime.load_plan(best_plan)
                outputs = runtime.run(steps=50)
                state = runtime.get_state()
                summary = runtime.monitor.summary()
                summary["status"] = state.status
                summary["active_modules"] = state.active_modules
                summary["events"] = state.events[-20:]
                st.session_state.runtime_result = {
                    "plan": best_plan,
                    "outputs": outputs,
                    "state": state,
                    "summary": summary,
                }
            st.success("Runtime运行完成!")

    with col_ctrl2:
        if (st.session_state.runtime_result is not None
                and st.button("注入模块故障 (模拟编码模块失败)", type="secondary")):
            result = st.session_state.runtime_result
            runtime = MicrokernelRuntime(registry=build_default_registry(), seed=42)
            runtime.load_plan(result["plan"])
            runtime.run(steps=5)
            runtime.inject_failure("code_conv_1_2")
            extra = runtime.run(steps=10)
            state = runtime.get_state()
            summary = runtime.monitor.summary()
            summary["status"] = state.status
            summary["events"] = state.events[-20:]
            result["outputs"].extend(extra)
            result["state"] = state
            result["summary"] = summary
            st.session_state.runtime_result = result
            st.warning(f"故障已注入! 当前状态: {state.status}")

    result = st.session_state.runtime_result
    if result is None:
        st.info("请点击「加载方案并运行50步」启动Runtime。")
        st.markdown("""
        ### 微内核Runtime概述
        
        微内核Runtime是AI-RAN系统的可信底座，负责：
        - **模块加载**：将AI生成的方案映射到实际通信模块
        - **运行监控**：实时收集BLER、吞吐量、时延等KPI
        - **安全守护**：检测异常并自动回退到安全模式 (BPSK + 高冗余)
        - **状态管理**：维护运行时状态和事件日志
        """)
        return

    plan = result["plan"]
    summary = result["summary"]
    state = result["state"]

    st.subheader("Runtime状态")
    status_color = "red" if summary.get("status") == "FALLBACK" else "green"
    st.markdown(f"**状态**: :{status_color}[{summary.get('status', 'N/A')}]")

    col_rt1, col_rt2, col_rt3, col_rt4 = st.columns(4)
    with col_rt1:
        st.metric("运行步数", summary.get("steps", 0))
    with col_rt2:
        st.metric("平均BLER", f"{summary.get('avg_bler', 0):.4f}")
    with col_rt3:
        st.metric("平均吞吐量", f"{summary.get('avg_throughput_kbps', 0):.1f} kbps")
    with col_rt4:
        st.metric("平均时延", f"{summary.get('avg_latency_ms', 0):.1f} ms")

    st.subheader("已加载模块")
    mods = summary.get("active_modules", [])
    if mods:
        module_labels = []
        for m in mods:
            label = m
            if "bpsk" in m:
                label = f"🟢 {m} (安全)"
            elif "64qam" in m:
                label = f"🟡 {m} (高速)"
            elif "16qam" in m:
                label = f"🟡 {m}"
            else:
                label = f"🔵 {m}"
            module_labels.append(label)
        for label in module_labels:
            st.markdown(f"- {label}")

    st.subheader("当前方案参数")
    col_pp1, col_pp2, col_pp3 = st.columns(3)
    with col_pp1:
        st.metric("调制", plan.modulation)
        st.metric("编码", f"{plan.coding_scheme} (R={plan.coding_rate:.2f})")
    with col_pp2:
        st.metric("HARQ重传", plan.harq_max_retx if plan.harq_enabled else "禁用")
        st.metric("导频密度", plan.pilot_density)
    with col_pp3:
        st.metric("调度器", plan.scheduler)
        st.metric("功率控制", plan.power_control)

    st.subheader("运行时KPI曲线")
    bler_vals = [o["kpi"]["bler"] for o in result["outputs"] if "kpi" in o]
    thr_vals = [o["kpi"]["throughput_kbps"] for o in result["outputs"] if "kpi" in o]
    lat_vals = [o["kpi"]["latency_ms"] for o in result["outputs"] if "kpi" in o]

    fig_kpi = go.Figure()
    fig_kpi.add_trace(go.Scatter(y=bler_vals, name="BLER", yaxis="y1"))
    fig_kpi.add_trace(go.Scatter(y=thr_vals, name="Throughput (kbps)", yaxis="y2"))
    fig_kpi.add_trace(go.Scatter(y=lat_vals, name="Latency (ms)", yaxis="y3"))
    fig_kpi.update_layout(
        title="Runtime KPI Evolution",
        yaxis=dict(title="BLER"),
        yaxis2=dict(title="Throughput (kbps)", overlaying="y", side="right"),
        yaxis3=dict(title="Latency (ms)", overlaying="y", side="right", position=0.95),
        height=400,
    )
    st.plotly_chart(fig_kpi, width="stretch")

    st.subheader("事件日志 (最近20条)")
    if summary.get("events"):
        st.dataframe(pd.DataFrame(summary["events"]))


def page_mock_sdr():
    st.title("模块5: Mock SDR半实物演示")
    st.caption("使用Mock SDR适配器模拟真实无线电的IQ波形生成、AWGN信道和频谱分析。")

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        modulation = st.selectbox("调制方式", ["BPSK", "QPSK", "16QAM", "64QAM"], index=1)
    with col_s2:
        snr_db = st.slider("SNR (dB)", -10, 30, 10, 1)
    with col_s3:
        n_symbols = st.number_input("符号数", 256, 4096, 1024, 256)

    if st.button("运行SDR测量", type="primary"):
        with st.spinner("Mock SDR运行中..."):
            sdr = MockSDRAdapter(seed=42)
            sdr.configure({"modulation": modulation, "snr_db": snr_db})
            st.session_state.sdr_metrics = sdr.measure_metrics()
            rx = sdr.receive()
            spectrum = sdr.measure_spectrum()
            st.session_state.sdr_waveform = {
                "rx_samples": rx,
                "spectrum": spectrum,
            }
        st.success("SDR测量完成!")

    metrics = st.session_state.sdr_metrics
    if metrics is None:
        st.info("请配置参数并点击「运行SDR测量」。")
        st.markdown("""
        ### Mock SDR概述
        
        Mock SDR提供了完整的半实物仿真环境：
        - **IQ波形生成**：BPSK/QPSK/16QAM/64QAM星座图映射
        - **AWGN信道**：模拟不同SNR下白高斯噪声影响
        - **频谱分析**：基于FFT的功率谱密度估计
        - **链路指标**：BER、EVM、丢包率、时延
        
        未来可通过GNU Radio适配器连接真实USRP设备。
        """)
        return

    st.subheader("SDR链路指标")
    col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
    with col_m1:
        st.metric("调制", metrics.get("modulation", "N/A"))
    with col_m2:
        st.metric("SNR", f"{metrics.get('snr_db', 0):.1f} dB")
    with col_m3:
        st.metric("BER", f"{metrics.get('ber', 0):.2e}")
    with col_m4:
        st.metric("EVM", f"{metrics.get('evm_percent', 0):.1f}%")
    with col_m5:
        st.metric("丢包率", f"{metrics.get('packet_loss', 0):.4f}")
    with col_m6:
        st.metric("时延", f"{metrics.get('latency_ms', 0):.1f} ms")

    waveform = st.session_state.get("sdr_waveform")
    if waveform:
        rx = waveform["rx_samples"]
        st.subheader("IQ星座图")
        fig_const = go.Figure()
        fig_const.add_trace(go.Scatter(
            x=rx.real[:500], y=rx.imag[:500],
            mode="markers",
            marker=dict(size=3, opacity=0.6),
            name="Received IQ",
        ))
        fig_const.update_layout(
            title=f"IQ Constellation ({modulation}, SNR={snr_db} dB)",
            xaxis_title="I",
            yaxis_title="Q",
            xaxis=dict(range=[-2, 2]),
            yaxis=dict(range=[-2, 2]),
            height=450,
        )
        st.plotly_chart(fig_const, width="stretch")

        spectrum = waveform["spectrum"]
        freqs = spectrum["freqs"]
        psd = spectrum["psd"]
        mid = len(freqs) // 2
        span = min(400, len(freqs) // 2)

        st.subheader("功率谱密度 (PSD)")
        fig_psd = go.Figure()
        fig_psd.add_trace(go.Scatter(
            x=freqs[mid - span:mid + span] / 1e3,
            y=psd[mid - span:mid + span],
            mode="lines",
            name="PSD",
        ))
        fig_psd.update_layout(
            title="Power Spectral Density (Normalized)",
            xaxis_title="Frequency (kHz, relative)",
            yaxis_title="Power (dB)",
            height=350,
        )
        st.plotly_chart(fig_psd, width="stretch")


def page_self_evolution():
    st.title("模块6: 自演进闭环优化")
    st.caption("多轮迭代演进：每轮基于上一轮KPI反馈自动优化策略，数据回流至Data Lake。")

    raw_intent = st.text_area(
        "初始意图",
        value="在 SNR 约为 10 dB 的城市宏基站场景下，要求 BLER < 5%，吞吐量 > 600 kbps，时延 < 30 ms。",
        height=80,
    )
    iterations = st.slider("迭代轮数", 1, 5, 3)

    if st.button("启动演进闭环", type="primary"):
        st.session_state.evolution_iterations = []
        loop = EvolutionLoop(seed=42, band_config=get_current_band_config())

        progress_bar = st.progress(0)
        for i in range(iterations):
            with st.spinner(f"第 {i + 1}/{iterations} 轮演进中..."):
                result = loop.run_once(raw_intent)
                st.session_state.evolution_iterations.append(result)
            progress_bar.progress((i + 1) / iterations)

        st.success(f"{iterations} 轮演进完成!")

    evo_iterations = st.session_state.get("evolution_iterations")

    if not evo_iterations:
        st.info("请配置初始意图和迭代轮数，然后点击「启动演进闭环」。")
        st.markdown("""
        ### 自演进闭环概述
        
        自演进闭环实现了AI-RAN的持续优化能力：
        - **经验收集**：每轮结果存入 Data Lake 进行持久化
        - **策略记忆**：按场景类型保存 Top-N 最优策略
        - **趋势分析**：可视化演进过程中KPI指标的变化趋势
        - **优化建议**：基于启发式规则生成下一轮优化方向
        
        闭环流程: Intention Input → AI Generate → DT Validate → Runtime Execute → Optimizer Suggest → Next Round
        """)

        st.subheader("历史经验数据")
        dl = DataLake()
        all_exp = dl.load_all()
        if all_exp:
            st.dataframe(pd.DataFrame(all_exp))
        else:
            st.info("暂无历史经验数据。")
        return

    st.subheader(f"演进趋势 ({len(evo_iterations)}轮)")
    bler_trend = [it["runtime_summary"].get("avg_bler", it["runtime_summary"].get("bler", 0))
                  for it in evo_iterations]
    thr_trend = [it["runtime_summary"].get("avg_throughput_kbps", it["runtime_summary"].get("throughput_kbps", 0))
                 for it in evo_iterations]
    lat_trend = [it["runtime_summary"].get("avg_latency_ms", it["runtime_summary"].get("latency_ms", 0))
                 for it in evo_iterations]
    scores = [it["best_twin_report"].final_score for it in evo_iterations]

    fig_evo = go.Figure()
    fig_evo.add_trace(go.Scatter(
        y=bler_trend, name="BLER", mode="lines+markers",
        yaxis="y1",
    ))
    fig_evo.add_trace(go.Scatter(
        y=thr_trend, name="Throughput (kbps)", mode="lines+markers",
        yaxis="y2",
    ))
    fig_evo.add_trace(go.Scatter(
        y=lat_trend, name="Latency (ms)", mode="lines+markers",
        yaxis="y3",
    ))
    fig_evo.add_trace(go.Bar(y=scores, name="Twin Score", opacity=0.3, yaxis="y4"))
    fig_evo.update_layout(
        title="Evolution KPI Trends",
        xaxis=dict(title="Iteration"),
        yaxis=dict(title="BLER"),
        yaxis2=dict(title="Throughput (kbps)", overlaying="y", side="right"),
        yaxis3=dict(title="Latency (ms)", overlaying="y", side="right", position=0.95),
        yaxis4=dict(title="Twin Score", overlaying="y", side="right", position=0.92, range=[0, 100]),
        height=400,
    )
    st.plotly_chart(fig_evo, width="stretch")

    for i, it in enumerate(evo_iterations):
        with st.expander(f"第 {i + 1} 轮详情"):
            plan = it["selected_plan"]
            summary = it["runtime_summary"]
            rec = it["recommendation"]

            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                st.markdown(f"**方案**: {plan.modulation} + {plan.coding_scheme}")
                st.markdown(f"**Twin评分**: {it['best_twin_report'].final_score:.1f}")
                st.markdown(f"**Twin决策**: {it['best_twin_report'].decision}")
            with col_d2:
                st.metric("BLER", f"{summary.get('avg_bler', 0):.4f}")
                st.metric("吞吐量", f"{summary.get('avg_throughput_kbps', 0):.1f} kbps")
            with col_d3:
                st.metric("时延", f"{summary.get('avg_latency_ms', 0):.1f} ms")
                st.metric("Runtime状态", summary.get("status", "N/A"))

            if rec:
                st.markdown("**优化建议**:")
                reasons = rec.get("reasons", [])
                for r in reasons:
                    st.markdown(f"- {r}")

    st.subheader("历史经验数据")
    dl = DataLake()
    all_exp = dl.load_all()
    if all_exp:
        st.dataframe(pd.DataFrame(all_exp))


def page_end_to_end():
    st.title("端到端：全流程一键演示")
    st.caption("一键运行 模块2 → 模块3 → 模块4 → 模块5 → 模块6 全流程，适合科研汇报演示。")

    raw_intent = st.text_area(
        "通信意图 (自然语言)",
        value="在 SNR 约为 10 dB 的城市宏基站场景下，要求 BLER < 5%，吞吐量 > 500 kbps，时延 < 50 ms。",
        height=100,
    )

    if st.button("启动端到端全流程演示", type="primary"):
        with st.spinner("全流程运行中 (AI编排 → 数字孪生验证 → Runtime运行 → SDR测量 → 演进优化)..."):
            report = run_end_to_end_demo(raw_intent, seed=42, band_config=get_current_band_config())
            st.session_state.end_to_end_result = report
        st.balloons()
        st.success("全流程演示完成!")

    report = st.session_state.end_to_end_result
    if report is None:
        st.info("请输入通信意图并点击「启动端到端全流程演示」。")
        st.markdown("""
        ### 全流程演示概述
        
        端到端流程一键运行以下所有阶段：
        
        1. **模块2 - AI编排**: 意图解析 → 环境分析 → 候选方案生成
        2. **模块3 - 数字孪生验证**: 接口检查 → 约束验证 → 链路仿真 → 故障注入 → 评分
        3. **模块4 - Runtime运行**: 方案加载 → 50步执行 → KPI监控 → 安全守护
        4. **模块5 - SDR半实物**: IQ波形生成 → AWGN信道 → 链路指标测量
        5. **模块6 - 自演进**: KPI反馈 → 优化建议 → 经验写入Data Lake
        
        **适用于**: 科研汇报、论文演示、项目进展展示。
        """)
        return

    st.subheader("演示总览")
    col_over1, col_over2, col_over3, col_over4 = st.columns(4)
    with col_over1:
        plans_count = len(report.candidate_plans)
        st.metric("AI生成候选方案", f"{plans_count} 个")
    with col_over2:
        score = report.selected_twin_report.get("final_score", 0)
        decision = report.selected_twin_report.get("decision", "N/A")
        twin_icon = "✅" if decision == "ACCEPT" else "❌"
        st.metric(f"数字孪生验证 {twin_icon}", f"评分: {score:.1f}")
    with col_over3:
        rt_status = report.runtime_summary.get("status", "N/A")
        rt_icon = "✅" if rt_status != "FALLBACK" else "🔴"
        st.metric(f"Runtime运行 {rt_icon}", rt_status)
    with col_over4:
        sdr_ber = report.sdr_summary.get("ber", 0)
        st.metric("SDR BER", f"{sdr_ber:.2e}")

    st.divider()

    st.subheader("Part 1: AI编排执行轨迹")
    for step in report.orchestration_trace:
        st.markdown(f"**{step['agent']}** → {step['message']}")

    st.subheader("Part 2: 数字孪生验证结果")
    for i, tr in enumerate(report.twin_reports):
        icon = "✅" if tr.get("decision") == "ACCEPT" else "❌"
        st.markdown(f"{icon} 方案 {i + 1}: {tr.get('plan_id', 'N/A')}, "
                     f"得分: {tr.get('final_score', 0):.1f}, "
                     f"决策: {tr.get('decision', 'N/A')}")

    st.subheader("Part 3: 选中方案详情")
    plan = report.selected_plan
    col_sp1, col_sp2, col_sp3 = st.columns(3)
    with col_sp1:
        st.markdown(f"**调制**: {plan.get('modulation', 'N/A')}")
        st.markdown(f"**编码**: {plan.get('coding_scheme', 'N/A')} (R={plan.get('coding_rate', 0):.2f})")
    with col_sp2:
        harq = plan.get('harq_enabled', False)
        st.markdown(f"**HARQ**: {'启用 (max=' + str(plan.get('harq_max_retx', 0)) + ')' if harq else '禁用'}")
        st.markdown(f"**导频**: {plan.get('pilot_density', 'N/A')}")
    with col_sp3:
        st.markdown(f"**调度器**: {plan.get('scheduler', 'N/A')}")
        st.markdown(f"**功率控制**: {plan.get('power_control', 'N/A')}")

    st.subheader("Part 4: Runtime KPI")
    col_rk1, col_rk2, col_rk3, col_rk4 = st.columns(4)
    summary = report.runtime_summary
    with col_rk1:
        st.metric("运行步数", summary.get("steps", 0))
    with col_rk2:
        st.metric("平均BLER", f"{summary.get('avg_bler', 0):.4f}")
    with col_rk3:
        st.metric("平均吞吐量", f"{summary.get('avg_throughput_kbps', 0):.1f} kbps")
    with col_rk4:
        st.metric("平均时延", f"{summary.get('avg_latency_ms', 0):.1f} ms")

    st.subheader("Part 5: SDR链路指标")
    col_sd1, col_sd2, col_sd3, col_sd4 = st.columns(4)
    sdr = report.sdr_summary
    with col_sd1:
        st.metric("BER", f"{sdr.get('ber', 0):.2e}")
    with col_sd2:
        st.metric("EVM", f"{sdr.get('evm_percent', 0):.1f}%")
    with col_sd3:
        st.metric("丢包率", f"{sdr.get('packet_loss', 0):.4f}")
    with col_sd4:
        st.metric("时延", f"{sdr.get('latency_ms', 0):.1f} ms")

    st.subheader("Part 6: 自演进优化建议")
    rec = report.evolution_recommendation
    if rec:
        reasons = rec.get("reasons", [])
        for r in reasons:
            st.markdown(f"- {r}")
        st.markdown(f"**预期改善**: {rec.get('expected_improvement', '')}")

    st.subheader("演示方案JSON (完整)")
    st.json(report.selected_plan)

    st.divider()
    st.success("全流程演示成功! 经验数据已写入 Data Lake。")


def page_algorithms():
    st.markdown("""
    <style>
    .alg-header {
        max-width: 960px;
        margin: 0 auto 8px;
    }
    .alg-header .alg-title {
        font-size: 30px;
        font-weight: 800;
        color: #1e40af;
        letter-spacing: -0.3px;
        line-height: 1.25;
    }
    .alg-header .alg-subtitle {
        font-size: 13px;
        color: #64748b;
        margin-top: 2px;
    }
    .alg-concept-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        margin: 8px 0 16px;
    }
    .alg-concept-table th {
        background: #f1f5f9;
        color: #334155;
        font-weight: 600;
        padding: 7px 10px;
        text-align: left;
        border-bottom: 2px solid #cbd5e1;
        font-size: 12px;
        letter-spacing: 0.3px;
    }
    .alg-concept-table td {
        padding: 7px 10px;
        border-bottom: 1px solid #e2e8f0;
        color: #475569;
        vertical-align: top;
    }
    .alg-concept-table tr:hover td {
        background: #f8fafc;
    }
    .alg-section-header {
        border-left: 3px solid #3b82f6;
        padding: 6px 14px;
        margin: 20px 0 10px;
        background: #f8fafc;
        border-radius: 0 6px 6px 0;
    }
    .alg-section-header h3 {
        margin: 0;
        color: #1e293b;
        font-size: 17px;
        font-weight: 700;
    }
    .alg-section-header p {
        margin: 2px 0 0;
        color: #64748b;
        font-size: 12px;
    }
    .alg-formula-box {
        background: #0f172a;
        color: #e2e8f0;
        padding: 12px 16px;
        border-radius: 8px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.7;
        margin: 10px 0;
        overflow-x: auto;
    }
    .alg-decision-flow {
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 10px 0;
        font-size: 13px;
        color: #0c4a6e;
        line-height: 1.8;
        font-family: 'Consolas', 'Courier New', monospace;
    }
    .alg-note {
        background: #fffbeb;
        border-left: 3px solid #f59e0b;
        padding: 8px 14px;
        border-radius: 0 6px 6px 0;
        font-size: 13px;
        color: #92400e;
        margin: 10px 0;
    }
    .alg-highlight {
        background: #ecfdf5;
        border-left: 3px solid #10b981;
        padding: 8px 14px;
        border-radius: 0 6px 6px 0;
        font-size: 13px;
        color: #065f46;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="alg-header">
        <div class="alg-title">系统核心算法介绍</div>
        <div class="alg-subtitle">AI 自演进 RAN 原型中所有关键算法的功能、输入输出与实现原理</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── 快速导航卡片 ──
    st.markdown('<p style="font-size:14px;font-weight:600;color:#475569;margin-bottom:8px;">📑 快速导航</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;height:100%;">
            <p style="font-size:12px;color:#3b82f6;font-weight:600;margin:0 0 4px;">📡 基础概念</p>
            <p style="font-size:11px;color:#64748b;margin:0;">SNR · SINR · BLER · MCS<br>调制 · 编码 · HARQ · 导频</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;height:100%;">
            <p style="font-size:12px;color:#3b82f6;font-weight:600;margin:0 0 4px;">⚙️ 通信算法</p>
            <p style="font-size:11px;color:#64748b;margin:0;">链路自适应 · KPI模型<br>信道建模 · 频段配置</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;height:100%;">
            <p style="font-size:12px;color:#3b82f6;font-weight:600;margin:0 0 4px;">🛡️ 数字孪生</p>
            <p style="font-size:11px;color:#64748b;margin:0;">校验 · 链路仿真<br>故障注入 · 评分决策</p>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;height:100%;">
            <p style="font-size:12px;color:#3b82f6;font-weight:600;margin:0 0 4px;">🔄 自演进</p>
            <p style="font-size:11px;color:#64748b;margin:0;">进化循环 · 启发式优化<br>波形 · 频谱 · BER</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ═══════════════ 第一部分：基础概念 ═══════════════
    st.markdown("""
    <div class="alg-section-header">
        <h3>一、通信基础概念速览</h3>
        <p>所有核心算法的基础概念定义。</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <table class="alg-concept-table">
    <thead><tr><th style="width:16%;">概念</th><th style="width:30%;">定义</th><th style="width:54%;">说明</th></tr></thead>
    <tbody>
    <tr><td><strong>SNR（信噪比）</strong></td><td>信号功率与噪声功率之比</td><td>衡量信号质量的直接指标，SNR 越高链路越可靠。单位：dB</td></tr>
    <tr><td><strong>SINR（信干噪比）</strong></td><td>信号功率与（干扰+噪声）功率之比</td><td>比 SNR 更全面的信道质量指标，是链路自适应决策的核心依据</td></tr>
    <tr><td><strong>BLER（误块率）</strong></td><td>传输块中错误块所占比例</td><td>衡量可靠性的核心指标，BLER=0.1 表示 10% 的块需重传</td></tr>
    <tr><td><strong>Throughput（吞吐量）</strong></td><td>单位时间内成功传输的数据量</td><td>有效传输速率。单位：kbps</td></tr>
    <tr><td><strong>Latency（时延）</strong></td><td>数据从发送到接收的延迟时间</td><td>包括传输时延、处理时延、排队时延。单位：ms</td></tr>
    <tr><td><strong>Modulation（调制）</strong></td><td>将比特序列映射到物理波形参量的技术</td><td>高阶调制每符号承载更多比特，但对信噪比要求更高</td></tr>
    <tr><td><strong>Coding Rate（编码率）</strong></td><td>信息比特数 / 总传输比特数</td><td>编码率越低冗余越多，纠错能力越强但有效速率越低</td></tr>
    <tr><td><strong>HARQ</strong></td><td>混合自动重传请求</td><td>结合前向纠错与自动重传的可靠性机制</td></tr>
    <tr><td><strong>MCS</strong></td><td>调制编码策略索引</td><td>调制方式与编码率的组合标识（0~28），越大越激进</td></tr>
    <tr><td><strong>Pilot（导频）</strong></td><td>收发双方已知的参考信号序列</td><td>用于接收端信道估计与均衡</td></tr>
    </tbody>
    </table>
    """, unsafe_allow_html=True)

    # ═══════════════ 第二部分：通信模块 ═══════════════
    st.markdown("""
    <div class="alg-section-header">
        <h3>二、通信模块算法</h3>
        <p>系统的通信功能由一组可插拔的模块组成，每个模块封装一种通信能力。</p>
    </div>
    """, unsafe_allow_html=True)

    # 2.1 调制
    with st.expander("📡 调制模块 — 算法功能 · 核心实现思路", expanded=True):
        st.markdown("**算法功能**：根据信道条件，在速率与可靠性之间权衡，选择合适的调制方式。每种调制方式定义了每符号携带的比特数。")
        st.markdown("**核心实现思路**：采用策略模式，每种调制预注册为独立模块实例（mod_bpsk / mod_qpsk / mod_16qam / mod_64qam），AI 按需加载到运行时上下文。")

        cL, cR = st.columns([1, 1])
        with cL:
            st.markdown("""
**四种调制方式参数：**

| 调制 | 比特/符号 | 最低SNR | 鲁棒性 | 适用场景 |
|------|----------|---------|--------|---------|
| BPSK | 1 | -2 dB | 1.0 | 远距离/高可靠 |
| QPSK | 2 | 3 dB | 0.8 | 均衡覆盖 |
| 16QAM | 4 | 9 dB | 0.5 | 近距离/较高吞吐 |
| 64QAM | 6 | 15 dB | 0.3 | 极近/最高吞吐 |
""")
        with cR:
            st.markdown("""
**输入/输出：**

| 输入 | 输出 |
|------|------|
| 调制名称 (str) | 调制方式 |
| 每符号比特数 (int) | bits_per_symbol |
| 鲁棒性系数 (float) | modulation_robustness |
""")

    # 2.2 编码
    with st.expander("🔐 信道编码模块 — 算法功能 · 核心实现思路", expanded=True):
        st.markdown("**算法功能**：在发送数据中引入冗余信息，使接收端具备检错和纠错能力。以编码率（信息比特/传输比特）衡量冗余度。")
        st.markdown("**核心实现思路**：系统预设三类编码方案（重复码/卷积码/LDPC），通过查表获取编码增益和处理时延，写入运行时上下文。编码率越低增益越高，但有效速率越低。")

        cL, cR = st.columns([1, 1])
        with cL:
            st.markdown("""
**六种编码方案参数：**

| 编码方案 | 编码率 | 增益 | 处理时延 |
|----------|--------|------|---------|
| Rep 1/3 | 0.33 | 5 dB | 15 ms |
| Rep 1/2 | 0.50 | 3 dB | 12 ms |
| Conv 1/2 | 0.50 | 3 dB | 8 ms |
| Conv 2/3 | 0.67 | 2 dB | 6 ms |
| LDPC 2/3 | 0.67 | 4 dB | 5 ms |
| LDPC 3/4 | 0.75 | 3 dB | 4 ms |
""")
        with cR:
            st.markdown("""
**编码类型说明：**
- **重复码**：数据重复传输，接收端多数投票判决。实现最简单
- **卷积码**：经典纠错码，中等复杂度与可靠性
- **LDPC**：低密度奇偶校验码，5G eMBB 标准编码方案，最优增益/冗余比
""")

    # 2.3 HARQ
    with st.expander("🔄 HARQ 重传模块 — 算法功能 · 核心实现思路", expanded=True):
        st.markdown("**算法功能**：当接收端检测到传输错误时，请求发送端重传数据。系统支持从无HARQ到增量冗余的多种配置。")
        st.markdown("**核心实现思路**：HARQ 的增益和代价由两个线性公式决定，基于通信理论中重传合并增益的简化建模。")
        st.markdown("""
**核心公式：**
""")
        st.markdown("""
<div class="alg-formula-box">
HARQ 增益 (dB) = 最大重传次数 × 1.2<br>
HARQ 时延代价 (ms) = 最大重传次数 × 8
</div>
""", unsafe_allow_html=True)
        st.markdown("""
| 重传次数 | 增益 | 时延代价 | 适用场景 |
|----------|------|---------|---------|
| 0（无HARQ） | 0 dB | 0 ms | 追求极低时延 |
| 1~2次 | 1.2~2.4 dB | 8~16 ms | 时延敏感 |
| 3~4次 | 3.6~4.8 dB | 24~32 ms | 高可靠性 |
""")

    # 2.4 导频
    with st.expander("📍 导频模块 — 算法功能 · 核心实现思路", expanded=True):
        st.markdown("**算法功能**：导频信号是收发双方约定的已知序列，接收端通过分析导频畸变估计信道状态。导频密度越高估计越准，但占用更多频谱资源。")
        st.markdown("**核心实现思路**：三档密度设计（low/medium/high），每档对应不同的信道估计增益和频谱效率折损。")
        cL, cR = st.columns([1, 1])
        with cL:
            st.markdown("""
**三档导频密度参数：**

| 密度 | 增益 | 频谱效率 | 适用场景 |
|------|------|---------|---------|
| high | +2 dB | 75% | 弱信号/高速移动 |
| medium | +1 dB | 88% | 一般信道条件 |
| low | 0 dB | 95% | 强信号/高吞吐 |
""")
        with cR:
            st.markdown("""
**输入/输出：**

| 输入 | 输出 |
|------|------|
| density (str): low/medium/high | pilot_density |
""")

    # 2.5 调度器
    with st.expander("📋 调度器模块 — 算法功能 · 核心实现思路", expanded=True):
        st.markdown("**算法功能**：决定多用户/多任务间的无线资源分配策略，不同的调度策略体现公平性、吞吐、可靠性和时延的权衡。")
        st.markdown("""
**核心实现思路**：每种调度策略预设不同的调度时延（体现调度算法复杂度），在实际系统中影响 MAC 层排队延迟。

| 调度策略 | 调度时延 | 设计理念 |
|----------|---------|---------|
| **throughput_first** | 5 ms | 优先分配资源给信道质量最优的用户 |
| **balanced** | 4 ms | 吞吐量与公平性折中 |
| **reliability_first** | 10 ms | 优先保障弱信号用户可靠性 |
| **latency_first** | 0 ms | 优先调度时延敏感数据，最小化排队延迟 |
""")

    # 2.6 功控 + 回退
    with st.expander("⚡ 功率控制与安全回退 — 算法功能 · 核心实现思路", expanded=True):
        st.markdown("**功率控制 — 算法功能**：决定发射功率的调节策略。直接决定信号覆盖范围、抗干扰能力和设备功耗。")
        st.markdown("**核心实现思路**：提供五种策略，从固定功率到基于SNR的动态调整，覆盖不同功耗-可靠性需求。")
        st.markdown("""
| 策略 | 设计理念 |
|------|---------|
| **fixed** | 固定功率输出，不随信道变化 |
| **snr_based** | 根据信道质量动态调整发射功率 |
| **conservative** | 偏向高功率保障链路可靠性 |
| **energy_saving** | 以最小功耗为目标，适合 IoT/卫星场景 |
""")
        st.markdown("**安全回退模块**：系统的最后防线。运行时监控到异常（如连续链路失败）时触发，强制切换为 BPSK + 1/3 码率 + 4 次 HARQ + 高导频 + 保守功控，牺牲效率换取最大可靠性。")

    # ═══════════════ 第三部分：链路自适应 ═══════════════
    st.markdown("""
    <div class="alg-section-header">
        <h3>三、链路自适应算法</h3>
        <p>根据实时信道质量，自动选择最优通信参数组合——这是系统的核心决策算法。</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔀 链路自适应 — 四档决策流程", expanded=True):
        st.markdown("**算法功能**：根据实时 SINR 和历史 BLER，自动选择最优的调制、编码、导频、HARQ 和功率参数组合。")
        st.markdown("**核心实现思路**：两步决策——先计算有效信道质量（含 BLER 惩罚修正），再通过四档阈值查表输出决策。BLER 惩罚机制使算法具有滞后性，避免频繁切换。")
        st.markdown("""
**第1步：计算有效信道质量**

<div class="alg-decision-flow">
质量参考值 = SINR（优先）或 SNR<br>
BLER 惩罚 = 如果上轮 BLER &gt; 目标 BLER，扣 2 dB<br>
<strong>有效质量 = 质量参考值 - BLER 惩罚</strong>
</div>

**第2步：四档决策表**

| 有效质量 | MCS | 调制 | 编码 | 码率 | 导频 | HARQ | 功率 | 级别 |
|----------|-----|------|------|------|------|------|------|------|
| ≥ 16 dB | 8 | 64QAM | LDPC | 0.75 | 6.25% | 0次 | 14 dBm | ✅ success |
| ≥ 10 dB | 6 | 16QAM | LDPC | 0.66 | 12.5% | 1次 | 16 dBm | ℹ️ info |
| ≥ 4 dB | 3 | QPSK | Conv | 0.50 | 12.5% | 2次 | 18 dBm | ⚠️ warning |
| < 4 dB | 1 | BPSK | Rep | 0.33 | 25% | 4次 | 20 dBm | 🔴 critical |
""")

    # ═══════════════ 第四部分：KPI ═══════════════
    st.markdown("""
    <div class="alg-section-header">
        <h3>四、KPI 估算模型</h3>
        <p>将信道质量和通信参数翻译成可度量的关键性能指标。</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📊 KPI 估算 — 从信道到指标的完整公式链", expanded=True):
        st.markdown("**算法功能**：输入信道质量和通信参数，输出 BLER、Throughput、Latency、频谱效率、可靠性等关键性能指标。")
        st.markdown("**核心实现思路**：五步串联计算——有效SINR → Sigmoid BLER → 吞吐量（含导频/HARQ效率折损）→ 时延（含HARQ/编码/导频开销）→ 可靠性。")
        st.markdown("**Sigmoid BLER 模型：**")
        st.markdown("""
<div class="alg-formula-box">
margin = 有效SINR - 调制所需最低SNR<br>
BLER = 1 / (1 + e<sup>0.9 × margin</sup>)<br>
BLER = clamp(BLER, 0.0001, 0.99)
</div>
""", unsafe_allow_html=True)

        st.markdown("**吞吐量公式：**")
        st.markdown("""
<div class="alg-formula-box">
频谱效率 = 调制阶数 × 编码率<br>
导频效率 = 1 - 导频密度<br>
HARQ效率 = 1 / (1 + 0.25 × 重传次数)<br>
包成功率 = 1 - BLER<br><br>
<strong>吞吐量(kbps) = 带宽(kHz) × 频谱效率 × 导频效率 × HARQ效率 × 包成功率</strong>
</div>
""", unsafe_allow_html=True)

        st.markdown("**时延公式：**")
        st.markdown("""
<div class="alg-formula-box">
<strong>时延(ms) = 10 + 4×HARQ重传 + 8×(1-编码率) + 2×导频密度</strong>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div class="alg-highlight">
<strong>Sigmoid 函数选择理由</strong>：真实通信中 BLER 不是阶跃函数，而是随着 SINR 下降呈现平滑的 S 形过渡。Sigmoid 使用参数 0.9 控制过渡斜率，并通过 [0.0001, 0.99] 截断避免极端值。
</div>
""", unsafe_allow_html=True)

    # ═══════════════ 第五部分：信道模型 ═══════════════
    st.markdown("""
    <div class="alg-section-header">
        <h3>五、信道模型算法</h3>
        <p>模拟真实无线信道的时间变化特性——7 种模式覆盖不同场景。</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🌊 信道模型 — 七种时变信道模式", expanded=True):
        st.markdown("**算法功能**：生成随时间变化的 SNR/SINR 序列，模拟真实无线传播环境中的不同场景。")
        st.markdown("**核心实现思路**：7 种信道模式各自实现独立的 SNR(step) 函数，通过随机种子保证可复现性。SINR = SNR - 干扰惩罚（有 jammer 时 3dB，正常 1dB），SNR 限制在 [-5, 30] dB。")
        cL, cR = st.columns(2)
        with cL:
            st.markdown("""
| 模式 | 模拟场景 | SNR 函数 |
|------|---------|---------|
| constant | 基线测试 | SNR 恒定不变 |
| linear_fading | 距离渐增 | SNR 线性下降 |
| sinusoidal | 多径衰落 | 正弦周期波动 |
""")
        with cR:
            st.markdown("""
| 模式 | 模拟场景 | SNR 函数 |
|------|---------|---------|
| random_walk | 真实噪声 | 随机游走 + 长期漂移 |
| blockage | 建筑物遮挡 | 骤降 → 持续 → 半恢复 |
| jamming_spike | 电子对抗 | 时段性强力干扰 |
| handover_like | 小区切换 | 降 → 稳 → 升 的 U 形 |
""")

        st.markdown("""
<div class="alg-formula-box">
<strong>随机游走模式</strong>（最接近真实环境）：<br>
SNR(step) = SNR(step-1) + drift + N(0, noise_std)<br>
drift = (final_SNR - initial_SNR) / total_steps
</div>
""", unsafe_allow_html=True)

    # ═══════════════ 第六部分：数字孪生 ═══════════════
    st.markdown("""
    <div class="alg-section-header">
        <h3>六、数字孪生五步验证</h3>
        <p>AI 方案部署前的安全验证引擎——五道关卡逐一审核。</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🛡️ 数字孪生 — 五步验证全流程", expanded=True):
        st.markdown("**算法功能**：在 AI 方案部署前进行五步安全验证——接口校验→约束校验→链路仿真→故障注入→评分决策，最终输出 ACCEPT/REJECT/NEED_REVISE 判定。")
        st.markdown("""
<div class="alg-decision-flow">
AI 方案 ──→ <strong>[1.接口校验]</strong> ──→ <strong>[2.约束校验]</strong> ──→ <strong>[3.链路仿真]</strong> ──→ <strong>[4.故障注入]</strong> ──→ <strong>[5.评分决策]</strong> ──→ ACCEPT / REJECT / REVISE
</div>

**第1步 — 接口校验**：检查 12 个必填字段是否完整存在且非空。

**第2步 — 约束校验**：
- 硬约束（不通过直接拒绝）：调制/编码在白名单内、编码率 [0.1, 0.95]、MCS [0, 28]、HARQ [0, 8]、功率 [0, 30] dBm、发射功率不超过任务上限
- 软约束（警告但不拒绝）：高可靠性任务+64QAM → 风险警告；低时延任务+高HARQ → 时延警告；节能任务+高功率 → 功耗警告；高吞吐任务+BPSK → 吞吐警告

**第3步 — 链路级仿真**（增益/惩罚叠加模型）：
""")
        st.markdown("""
<div class="alg-formula-box">
有效SINR = 环境SINR - 频率惩罚 + 编码增益 + 导频增益 + HARQ增益 + 功率增益 - 调制惩罚 + 干扰补偿<br><br>
HARQ增益 = 重传次数 × 1.2 dB<br>
功率增益 = clamp((功率 - 10) / 5, 0, 4) dB<br><br>
BLER = 1 / (1 + e<sup>(有效SINR - 调制阈值) / 2</sup>)<br>
能耗 = 10<sup>功率/10</sup> / 1000 × (1 + 0.05 × HARQ次数)
</div>
""", unsafe_allow_html=True)

        st.markdown("""
**第4步 — 故障注入**（测试方案鲁棒性，5 种异常注入）：

| 故障类型 | 注入操作 | 模拟场景 |
|----------|---------|---------|
| sudden_snr_drop | SNR/SINR 各 -10 dB | 突发信号严重衰减 |
| burst_interference | SINR -5 dB，干扰→high | 突发强干扰 |
| high_mobility | 多普勒×3，SINR -2 dB | 高速移动 |
| power_limit | SINR -3 dB | 功率受限 |
| module_failure | SINR -8 dB | 通信模块故障 |

**第5步 — 加权评分**（根据任务优先级动态分配权重）：

| 优先级 | 可靠性 | 吞吐量 | 时延 | 能耗 | 鲁棒性 |
|--------|--------|--------|------|------|--------|
| reliability | 40% | 15% | 15% | 10% | 20% |
| throughput | 15% | **45%** | 15% | 10% | 15% |
| latency | 20% | 15% | **40%** | 10% | 15% |
| energy | 20% | 15% | 10% | **40%** | 15% |
| anti_jamming | 30% | 15% | 15% | 5% | **35%** |

**核心实现思路**：各子评分采用比率模型（实际/目标 或 目标/实际），得分 ∈ [0, 100]。鲁棒性得分由故障条件下 BLER 指标（60%）和吞吐保持率（40%）组成。最终加权总分决定决策。

**最终判定**：
- 得分 ≥ 75 且链路仿真通过且故障测试通过（鲁棒性 ≥ 40）→ **ACCEPT**
- 得分 ≥ 60 → **NEED_REVISE**
- 否则 → **REJECT**
""")

    # ═══════════════ 第七部分：自演进 ═══════════════
    st.markdown("""
    <div class="alg-section-header">
        <h3>七、自演进与优化算法</h3>
        <p>发现问题→分析瓶颈→生成建议→下一轮优化，形成自我改进闭环。</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔄 进化循环与启发式优化 — 算法功能 · 核心实现思路", expanded=True):
        st.markdown("**算法功能**：实现自演进闭环——AI 生成方案 → 孪生验证 → 择优执行 → 监控 KPI → 分析瓶颈 → 生成优化建议 → 下一轮迭代。")
        st.markdown("""
**核心实现思路**：

<div class="alg-decision-flow">
<strong>单次循环</strong>：AI 编配(生成意图+环境+候选) → 数字孪生验证 → 选 ACCEPT 中最高分 → 微内核运行 50 步 → 监控收集 KPI → 启发式分析瓶颈 → 记录到 DataLake → 更新策略记忆<br><br>
<strong>多轮迭代</strong>：每轮根据瓶颈调整下轮意图——BLER 超标 → 强调可靠性；吞吐不足 → 强调吞吐量；时延超标 → 强调低时延
</div>

**启发式诊断逻辑**（基于 KPI-目标对比的规则推理）：

| 诊断条件 | 推荐的优化方向 |
|----------|--------------|
| BLER > 目标 BLER | 降低调制阶数、提升导频密度、增加 HARQ 重传、适度提高发射功率 |
| 吞吐量 < 最小吞吐 | 提高调制阶数、提高编码率、降低导频和 HARQ 开销 |
| 时延 > 最大时延 | 减少 HARQ 重传、切换 latency_first 调度器、选择低复杂度编码 |
| 无瓶颈 | 保持当前策略、小幅优化 MCS、继续收集数据 |

**历史策略推荐**：从 DataLake 中检索该场景类型下历史最高得分的 N 条策略作为参考基线。
""")

    # ═══════════════ 第八部分：频段 ═══════════════
    st.markdown("""
    <div class="alg-section-header">
        <h3>八、频段配置算法</h3>
        <p>模拟真实 5G 频段（n41/n79）的物理特性对通信性能的影响。</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📶 频段配置 — 算法功能 · 核心实现思路", expanded=True):
        st.markdown("**算法功能**：管理预设频段配置（n41/n79/自定义），基于 Friis 传播模型计算频率对链路性能的惩罚因子，并注入到 KPI 和链路仿真中。")
        st.markdown("**核心实现思路**：基准频率取 2600MHz（n41），惩罚 = 20·log₁₀(f/f₀)。此惩罚直接扣减有效 SINR，进而影响 BLER 和吞吐量。")
        cL, cR = st.columns(2)
        with cL:
            st.markdown("""
**频率惩罚公式：**

<div class="alg-formula-box">
频率惩罚 (dB) = 20 × log₁₀(载波频率 / 2600)
</div>

**物理基础**：Friis 自由空间传播模型——信号衰减与频率平方成正比。
""")
        with cR:
            st.markdown("""
**频段对比：**

| 频段 | 中心频率 | 惩罚 | 典型场景 |
|------|---------|------|---------|
| n41 | 2600 MHz | 0 dB | 中国移动主力覆盖 |
| n79 | 4900 MHz | ≈ 5.5 dB | 高速热点覆盖 |

n79 同等条件下比 n41 弱约 5.5 dB，需更高基站密度补偿。
""")

    # ═══════════════ 第九部分：波形 ═══════════════
    st.markdown("""
    <div class="alg-section-header">
        <h3>九、波形生成与频谱分析</h3>
        <p>从比特到电磁波——IQ 符号生成、噪声叠加、频谱分析和误码率估算。</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("〰️ 波形与频谱 — 算法功能 · 核心实现思路", expanded=True):
        st.markdown("**算法功能**：生成调制符号（IQ平面星座点）、叠加 AWGN 噪声、估计功率谱密度、快速估算 BER/EVM/丢包率。")
        st.markdown("""
**核心实现思路**：
- **IQ 符号生成**：基于标准星座映射，使用归一化因子保证平均能量为 1（BPSK:1, QPSK:1/√2, 16QAM:1/√10, 64QAM:1/√42）
- **AWGN 叠加**：噪声功率 = 信号功率 / 10^(SNR/10)，生成复高斯噪声后相加
- **PSD 估计**：Hanning 窗 + FFT → 频域 → 20·log₁₀|spectrum|
- **BER 估算**：AWGN 信道下各调制方式的工程简化近似公式
""")
        st.markdown("""
**IQ 符号生成：**

| 调制 | 星座点 | 归一化因子 |
|------|--------|-----------|
| BPSK | {-1, +1} | 1 |
| QPSK | 45°/135°/225°/315° | 1/√2 |
| 16QAM | {±1,±3} × {±1,±3} | 1/√10 |
| 64QAM | {±1,±3,±5,±7}² | 1/√42 |

**AWGN 噪声叠加：**
""")
        st.markdown("""
<div class="alg-formula-box">
噪声功率 = 信号功率 / 10<sup>SNR/10</sup><br>
噪声 = √(噪声功率/2) × [N(0,1) + j·N(0,1)]<br>
输出 = 信号 + 噪声
</div>
""", unsafe_allow_html=True)

        st.markdown("""
**功率谱密度估计**：FFT + Hanning 窗 → 时域转频域 → 20·log₁₀|FFT| → dB 单位功率谱。

**简化 BER 估算公式**（AWGN 信道工程近似）：

| 调制 | BER ≈ |
|------|-------|
| BPSK | 0.5 · e^(-SNR_linear) |
| QPSK | 0.7 · e^(-0.8 · SNR_linear) |
| 16QAM | e^(-0.25 · SNR_linear) |
| 64QAM | e^(-0.12 · SNR_linear) |

**EVM 估算**：EVM(%) = 100 / √SNR_linear  
**丢包率**：PLR = 1 - (1 - BER)^1000（假设每包 1000 比特的简化模型）
""")

    # ═══════════════ 附录：索引 ═══════════════
    st.markdown("""
    <div class="alg-section-header">
        <h3>附录：算法索引表</h3>
        <p>26 个核心算法/模型快速索引。</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 完整算法索引（共 26 项）", expanded=False):
        alg_index = [
            ("调制模块", "modulation.py", "通信模块", "决定每符号比特数"),
            ("信道编码模块", "coding.py", "通信模块", "冗余纠错"),
            ("HARQ重传模块", "harq.py", "通信模块", "失败自动重传"),
            ("导频模块", "pilot.py", "通信模块", "信道估计参考信号"),
            ("调度器模块", "scheduler.py", "通信模块", "资源分配策略"),
            ("功率控制模块", "power_control.py", "通信模块", "发射功率调节"),
            ("安全回退模块", "fallback.py", "通信模块", "异常安全保护"),
            ("链路自适应", "adaptation.py", "仿真核心", "4档决策选择通信参数"),
            ("KPI估算模型", "kpi_model.py", "仿真核心", "量化通信性能指标"),
            ("信道时间线", "channel_timeline.py", "仿真核心", "7种信道环境模拟"),
            ("KPI记录器", "kpi_recorder.py", "仿真核心", "时序KPI数据管理"),
            ("实验运行器", "experiment.py", "仿真核心", "仿真顶层调度"),
            ("接口校验", "validators.py", "数字孪生", "字段完整性和约束检查"),
            ("约束校验", "validators.py", "数字孪生", "参数范围与任务匹配检查"),
            ("链路级仿真", "link_simulator.py", "数字孪生", "增益/惩罚叠加仿真"),
            ("故障注入", "fault_injection.py", "数字孪生", "5种异常模拟"),
            ("综合评分", "scoring.py", "数字孪生", "加权多目标评分"),
            ("沙盒决策", "sandbox.py", "数字孪生", "ACCEPT/REJECT判定"),
            ("进化循环", "evolution_loop.py", "自演进", "多轮迭代自优化"),
            ("启发式优化", "optimizer.py", "自演进", "KPI对比规则推荐"),
            ("历史推荐", "recommender.py", "自演进", "历史最优策略检索"),
            ("频段配置", "band_config.py", "公共工具", "频率惩罚计算"),
            ("IQ符号生成", "waveform.py", "SDR", "BPSK/QPSK/QAM符号"),
            ("AWGN噪声", "waveform.py", "SDR", "加性白高斯噪声"),
            ("功率谱估计", "spectrum.py", "SDR", "FFT频谱分析"),
            ("BER估算", "mock_sdr.py", "SDR", "简化误码率公式"),
        ]
        for i, (name, file, module, desc) in enumerate(alg_index, 1):
            cN, cF, cM, cD = st.columns([0.2, 1.2, 1, 2.6])
            bg = "#f8fafc" if i % 2 == 0 else "#ffffff"
            with cN:
                st.markdown(f'<p style="background:{bg};padding:5px 8px;margin:0;font-size:12px;color:#94a3b8;">{i}</p>', unsafe_allow_html=True)
            with cF:
                st.markdown(f'<p style="background:{bg};padding:5px 8px;margin:0;font-size:12px;"><strong>{name}</strong></p>', unsafe_allow_html=True)
            with cM:
                st.markdown(f'<p style="background:{bg};padding:5px 8px;margin:0;font-size:11px;color:#64748b;">{file}</p>', unsafe_allow_html=True)
            with cD:
                st.markdown(f'<p style="background:{bg};padding:5px 8px;margin:0;font-size:11px;color:#475569;">{module} · {desc}</p>', unsafe_allow_html=True)

    st.divider()
    st.caption("算法文档版本：Alpha 1.0 · 覆盖 26 个核心算法/模型 · 持续更新中")


def main():
    init_session_state()

    with st.sidebar:
        st.image("LOGO.jpg", width=90)
        st.markdown("""
        <div style="margin-bottom:4px;">
            <div style="font-weight:700;font-size:15px;color:#1e293b;line-height:1.3;">
                AI-Native RAN
            </div>
            <div style="font-size:10px;color:#64748b;line-height:1.4;margin-top:1px;">
                Microkernel-based<br>Self-Evolving RAN Prototype
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.caption(
            "基于通信微内核的 AI 自设计、自验证、"
            "自运行、自演进原型平台。"
        )

        st.divider()

        page = st.radio(
            "导航",
            PAGES,
            index=0,
        )

        st.divider()

        band_labels = {
            "n41_100mhz": "n41 2.6GHz 100MHz（移动主力）",
            "n79_100mhz": "n79 4.9GHz 100MHz（高速热点）",
            "n41_50mhz": "n41 2.6GHz 50MHz",
            "sim_default": "仿真默认 500kHz",
        }
        band_keys = list(band_labels.keys())
        current_idx = band_keys.index(st.session_state.band_key) if st.session_state.band_key in band_keys else 0
        selected_key = st.selectbox(
            "频段配置",
            band_keys,
            index=current_idx,
            format_func=lambda k: band_labels[k],
            key="main_band_select",
        )
        if selected_key != st.session_state.band_key:
            st.session_state.band_key = selected_key
            band_cfg = get_band_config(selected_key)
            st.session_state.research_controller.set_band_config(band_cfg)
            st.rerun()

        with st.expander("自定义"):
            custom_bw = st.slider("带宽 MHz", 1, 200, 100, 10, key="main_custom_bw")
            custom_freq = st.slider("频率 MHz", 700, 6000, 2600, 100, key="main_custom_freq")
            if st.button("应用", key="main_apply_custom", use_container_width=True):
                custom_cfg = build_custom_band(st.session_state.main_custom_freq, st.session_state.main_custom_bw)
                st.session_state.band_key = "custom"
                st.session_state.research_controller.set_band_config(custom_cfg)
                st.rerun()

        if st.session_state.band_key == "custom":
            band_cfg = build_custom_band(st.session_state.main_custom_freq, st.session_state.main_custom_bw)
        else:
            band_cfg = get_band_config(st.session_state.band_key)
        st.caption(
            f"{band_cfg.name}  {band_cfg.carrier_freq_mhz:.0f}MHz  "
            f"{band_cfg.bandwidth_mhz:.0f}MHz  "
            f"Δ{band_cfg.freq_penalty_db:+.1f}dB"
        )

    if page == PAGES[0]:
        page_home()
    elif page == PAGES[1]:
        page_algorithms()
    elif page == PAGES[2]:
        page_phase1_simulation()
    elif page == PAGES[3]:
        page_ai_orchestration()
    elif page == PAGES[4]:
        page_digital_twin()
    elif page == PAGES[5]:
        page_runtime()
    elif page == PAGES[6]:
        page_mock_sdr()
    elif page == PAGES[7]:
        page_self_evolution()
    elif page == PAGES[8]:
        page_end_to_end()


if __name__ == "__main__":
    st.set_page_config(
        page_title="AI-Native RAN (Microkernel-based Self-Evolving RAN Prototype)",
        page_icon=":satellite_antenna:",
        layout="wide",
    )
    main()
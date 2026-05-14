import React, { useState } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { ConfigProvider, Layout, Card, Row, Col, Button, Typography, Space, Drawer, message } from 'antd';
import { SearchOutlined, EditOutlined, MenuOutlined, ThunderboltOutlined } from '@ant-design/icons';
import QueryPanel from './components/QueryPanel';
import DataEntry from './components/DataEntry';
import StudentForm from './components/StudentForm';
import RecommendationList from './components/RecommendationList';
import VolunteerTable from './components/VolunteerTable';
import notionTheme from './notion-theme';
import './App.css';

const { Header, Content, Footer } = Layout;
const { Title, Text } = Typography;

// ====== 首页 ======
function HomePage() {
  const navigate = useNavigate();

  const features = [
    {
      key: 'query',
      title: '数据查询',
      icon: <SearchOutlined style={{ fontSize: 20, color: '#37352F' }} />,
      iconBg: '#E8F0FE',
      description: '按院校、专业、位次查询历年录取分数和位次信息',
      action: '进入查询',
      emoji: '🔍'
    },
    {
      key: 'simulator',
      title: '志愿模拟填报',
      icon: <ThunderboltOutlined style={{ fontSize: 20, color: '#37352F' }} />,
      iconBg: '#E6F7EC',
      description: '录入分数和偏好，智能推荐冲/稳/保三层志愿方案',
      action: '开始填报',
      emoji: '🧠'
    },
    {
      key: 'data-entry',
      title: '数据录入',
      icon: <EditOutlined style={{ fontSize: 20, color: '#37352F' }} />,
      iconBg: '#FEF3E2',
      description: '管理院校信息，录入历年录取分数和一分一段表',
      action: '进入录入',
      emoji: '📋'
    },
  ];

  return (
    <div style={{ maxWidth: 960, margin: '0 auto' }}>
      {/* 欢迎区 */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 12, color: '#B4B4B0', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>
          云志选 · 高考志愿决策系统
        </div>
        <Title level={2} style={{ margin: 0 }}>欢迎回来</Title>
        <Text type="secondary" style={{ fontSize: 14, marginTop: 4, display: 'block' }}>
          2026 云南省物理类考生 · 基于历年录取数据的智能决策
        </Text>
      </div>

      {/* 数据概览卡片 */}
      <Row gutter={[12, 12]} style={{ marginBottom: 24 }}>
        {[
          { num: 186, label: '可报高校', sub: '云南省物理类 · 本科批', color: '#2F8CFF' },
          { num: '1,247', label: '可报专业', sub: '含 985/211 院校 43 所', color: '#3CB371' },
          { num: 8, label: '我的收藏', sub: '3 所待详细对比', color: '#E8A838' },
        ].map((s, i) => (
          <Col xs={24} sm={8} key={i}>
            <div className="notion-stat-card">
              <div className="notion-stat-num" style={{ color: s.color }}>{s.num}</div>
              <div className="notion-stat-label">{s.label}</div>
              <div className="notion-stat-sub">{s.sub}</div>
            </div>
          </Col>
        ))}
      </Row>

      {/* 功能入口 */}
      <Row gutter={[12, 12]}>
        {features.map(f => (
          <Col xs={24} sm={8} key={f.key}>
            <div className="notion-action-card" onClick={() => navigate(`/${f.key === 'simulator' ? 'simulator' : f.key === 'query' ? 'query' : 'data-entry'}`)}>
              <div className="notion-action-icon" style={{ background: f.iconBg }}>
                {f.icon}
              </div>
              <div className="notion-action-body">
                <div className="notion-action-title">{f.emoji} {f.title}</div>
                <div className="notion-action-desc">{f.description}</div>
              </div>
            </div>
          </Col>
        ))}
      </Row>

      {/* 快速推荐 */}
      <div style={{ marginTop: 32 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: '#9B9A97', marginBottom: 8 }}>
          最近浏览 / 推荐
        </div>
        {[
          { name: '云南大学', tag: '211 · 双一流', loc: '昆明', prob: 85 },
          { name: '昆明理工大学', tag: '省重点', loc: '昆明', prob: 62 },
          { name: '浙江大学', tag: '985 · 双一流', loc: '杭州', prob: 12 },
        ].map((item, i) => (
          <div className="notion-list-item" key={i} onClick={() => navigate('/query')}>
            <div className="notion-list-left">
              <span style={{ fontSize: 16, marginRight: 8 }}>🏛️</span>
              <span style={{ fontWeight: 500 }}>{item.name}</span>
              <span className="notion-tag">{item.tag}</span>
            </div>
            <div className="notion-list-right">
              <span style={{ fontSize: 12, color: '#9B9A97' }}>{item.loc}</span>
              <div className="notion-prob-bar">
                <div className="notion-prob-fill"
                  style={{ width: `${item.prob}%`, background: item.prob >= 70 ? '#3CB371' : item.prob >= 40 ? '#E8A838' : '#E25C5C' }}
                />
              </div>
              <span style={{ fontSize: 12, color: item.prob >= 70 ? '#3CB371' : item.prob >= 40 ? '#E8A838' : '#E25C5C' }}>
                {item.prob >= 70 ? '高概率' : item.prob >= 40 ? '中等概率' : '低概率'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ====== 志愿模拟填报 ======
function SimulatorPage() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [studentInfo, setStudentInfo] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  const steps = [
    { title: '录入信息', content: <StudentForm onSubmit={handleStudentSubmit} /> },
    { title: '智能推荐', content: <RecommendationList recommendations={recommendations} onGenerateVolunteerTable={() => setCurrentStep(2)} /> },
    { title: '志愿方案', content: <VolunteerTable studentInfo={studentInfo} recommendations={recommendations} /> },
  ];

  async function handleStudentSubmit(values) {
    try {
      const response = await fetch('/api/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });
      const data = await response.json();
      setStudentInfo(values);
      setRecommendations(data.recommendations);
      setCurrentStep(1);
      message.success('推荐生成成功！');
    } catch (error) {
      message.error('生成推荐失败：' + error.message);
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <div style={{ marginBottom: 24 }}>
        <div style={{ fontSize: 12, color: '#B4B4B0', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 4 }}>
          志愿填报
        </div>
        <Title level={3} style={{ margin: 0 }}>模拟填报</Title>
      </div>

      {/* Notion 风格步骤条 */}
      <div className="notion-steps">
        {steps.map((s, i) => (
          <React.Fragment key={i}>
            <div
              className={`notion-step ${i <= currentStep ? 'active' : ''} ${i < currentStep ? 'done' : ''}`}
              onClick={() => { if (i <= currentStep) setCurrentStep(i); }}
            >
              <div className="notion-step-circle">
                {i < currentStep ? '✓' : i + 1}
              </div>
              <div className="notion-step-label">{s.title}</div>
            </div>
            {i < steps.length - 1 && <div className={`notion-step-line ${i < currentStep ? 'done' : ''}`} />}
          </React.Fragment>
        ))}
      </div>

      <div style={{ marginTop: 32 }}>
        {steps[currentStep].content}
      </div>
    </div>
  );
}

// ====== App ======
function App() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const navLinks = [
    { to: '/', label: '首页' },
    { to: '/query', label: '数据查询' },
    { to: '/simulator', label: '志愿填报' },
    { to: '/data-entry', label: '数据录入' },
  ];

  return (
    <ConfigProvider theme={notionTheme}>
      <Layout style={{ minHeight: '100vh' }}>
        {/* Notion 风格顶栏 */}
        <Header className="notion-app-header">
          <Link to="/" className="notion-app-logo">
            <span className="notion-app-logo-icon">云</span>
            <span className="notion-app-logo-text">云志选</span>
          </Link>

          <Space size={2} className="notion-desktop-nav">
            {navLinks.map(n => (
              <Link key={n.to} to={n.to} className={`notion-nav-link ${window.location.pathname === n.to ? 'active' : ''}`}>
                {n.label}
              </Link>
            ))}
          </Space>

          <Button
            type="text"
            icon={<MenuOutlined />}
            className="notion-mobile-btn"
            onClick={() => setDrawerOpen(true)}
          />
        </Header>

        <Drawer
          title={<span style={{ fontWeight: 500 }}>云志选</span>}
          placement="right"
          onClose={() => setDrawerOpen(false)}
          open={drawerOpen}
          width={220}
          bodyStyle={{ padding: 8 }}
        >
          {navLinks.map(n => (
            <Link key={n.to} to={n.to} style={{
              display: 'block', padding: '8px 12px', borderRadius: 4,
              color: window.location.pathname === n.to ? '#2F8CFF' : '#37352F',
              background: window.location.pathname === n.to ? '#E8F0FE' : 'transparent',
              fontSize: 14, marginBottom: 2, textDecoration: 'none',
            }} onClick={() => setDrawerOpen(false)}>
              {n.label}
            </Link>
          ))}
        </Drawer>

        <Content style={{ padding: '32px 24px', background: '#F7F6F3' }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/query" element={<QueryPanel />} />
            <Route path="/simulator" element={<SimulatorPage />} />
            <Route path="/data-entry" element={<DataEntry />} />
          </Routes>
        </Content>

        <Footer style={{
          textAlign: 'center',
          padding: '16px 24px',
          fontSize: 12,
          color: '#B4B4B0',
          borderTop: '1px solid #EBE9E4',
          background: '#F7F6F3',
        }}>
          云志选 ©2026 · 云南高考志愿决策系统
        </Footer>
      </Layout>
    </ConfigProvider>
  );
}

export default App;

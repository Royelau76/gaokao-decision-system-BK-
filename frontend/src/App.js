import React, { useState } from 'react';
import { Layout, Card, Row, Col, Button, Typography, Space, message } from 'antd';
import { SearchOutlined, EditOutlined, ArrowLeftOutlined, ExperimentOutlined, HolderOutlined } from '@ant-design/icons';
import QueryPanel from './components/QueryPanel';
import DataEntry from './components/DataEntry';
import StudentForm from './components/StudentForm';
import RecommendationList from './components/RecommendationList';
import VolunteerTable from './components/VolunteerTable';
import './App.css';

const { Header, Content, Footer } = Layout;
const { Title, Paragraph } = Typography;

// ====== 首页 ======
function HomePage({ onNavigate }) {
  const features = [
    {
      key: 'query',
      title: '数据查询',
      icon: <SearchOutlined style={{ fontSize: 48, color: '#1890ff' }} />,
      description: '按院校、专业、位次查询历年录取分数和位次信息，快速了解目标院校的录取情况。',
      action: '进入查询'
    },
    {
      key: 'simulator',
      title: '志愿模拟填报',
      icon: <EditOutlined style={{ fontSize: 48, color: '#52c41a' }} />,
      description: '录入分数和偏好，系统基于历年数据智能推荐冲/稳/保三层志愿方案，一键导出。',
      action: '开始填报'
    },
    {
      key: 'data-entry',
      title: '数据录入',
      icon: <EditOutlined style={{ fontSize: 48, color: '#fa8c16' }} />,
      description: '管理院校信息，录入历年录取分数和一分一段表，支持CSV批量导入导出。',
      action: '进入录入'
    },
  ];

  return (
    <div style={{ maxWidth: 900, margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: 48 }}>
        <Title level={2}>🎯 云志选 - 2026云南高考志愿决策系统</Title>
        <Paragraph type="secondary" style={{ fontSize: 16 }}>
          基于历年录取数据的智能志愿填报辅助平台
        </Paragraph>
      </div>

      <Row gutter={24}>
        {features.map(f => (
          <Col span={12} key={f.key}>
            <Card
              hoverable
              style={{ textAlign: 'center', height: '100%', borderRadius: 8 }}
              bodyStyle={{ padding: '32px 24px' }}
            >
              <div style={{ marginBottom: 16 }}>{f.icon}</div>
              <Title level={3}>{f.title}</Title>
              <Paragraph type="secondary" style={{ minHeight: 60 }}>
                {f.description}
              </Paragraph>
              <Button
                type="primary"
                size="large"
                onClick={() => onNavigate(f.key)}
                style={{ borderRadius: 6 }}
              >
                {f.action}
              </Button>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}

// ====== 志愿模拟填报子页面 ======
function SimulatorPage({ onBack }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [studentInfo, setStudentInfo] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  const steps = [
    { title: '录入信息', content: (
      <StudentForm onSubmit={handleStudentSubmit} />
    )},
    { title: '智能推荐', content: (
      <RecommendationList
        recommendations={recommendations}
        onGenerateVolunteerTable={() => setCurrentStep(2)}
      />
    )},
    { title: '志愿方案', content: (
      <VolunteerTable studentInfo={studentInfo} recommendations={recommendations} />
    )},
    { title: '导出方案', content: (
      <ExportPlan studentInfo={studentInfo} recommendations={recommendations} />
    )},
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
    <div>
      <div style={{ marginBottom: 24 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={onBack}>返回首页</Button>
      </div>

      <Card>
        {/* Simple step indicator */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 32 }}>
          {steps.map((s, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center',
              opacity: i <= currentStep ? 1 : 0.35,
              cursor: i <= currentStep ? 'pointer' : 'default'
            }} onClick={() => { if (i <= currentStep) setCurrentStep(i); }}>
              <div style={{
                width: 32, height: 32, borderRadius: '50%',
                background: i <= currentStep ? '#1890ff' : '#d9d9d9',
                color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 'bold', fontSize: 14
              }}>
                {i + 1}
              </div>
              <span style={{ margin: '0 8px', fontSize: 14, color: i <= currentStep ? '#333' : '#bbb' }}>
                {s.title}
              </span>
              {i < steps.length - 1 && (
                <div style={{
                  width: 40, height: 2,
                  background: i < currentStep ? '#1890ff' : '#e8e8e8',
                  marginRight: 8
                }} />
              )}
            </div>
          ))}
        </div>

        <div style={{ marginTop: 40 }}>
          {steps[currentStep].content}
        </div>
      </Card>
    </div>
  );
}

function ExportPlan({ studentInfo, recommendations }) {
  const handleExport = () => {
    const data = {
      studentInfo,
      recommendations,
      exportTime: new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `志愿方案_${studentInfo?.score}分_${new Date().toLocaleDateString()}.json`;
    a.click();
    message.success('方案已导出！');
  };

  return (
    <div style={{ textAlign: 'center', padding: '40px' }}>
      <h2>导出志愿方案</h2>
      <p>将您的志愿方案保存到本地</p>
      <button onClick={handleExport} style={{
        padding: '10px 30px', fontSize: '16px', background: '#1890ff',
        color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer'
      }}>
        导出JSON文件
      </button>
    </div>
  );
}

// ====== App 根组件 ======
function App() {
  const [page, setPage] = useState('home');

  const renderPage = () => {
    switch (page) {
      case 'query':
        return (
          <div>
            <div style={{ marginBottom: 24 }}>
              <Button icon={<ArrowLeftOutlined />} onClick={() => setPage('home')}>返回首页</Button>
            </div>
            <QueryPanel />
          </div>
        );
      case 'simulator':
        return <SimulatorPage onBack={() => setPage('home')} />;
      case 'data-entry':
        return (
          <div>
            <div style={{ marginBottom: 24 }}>
              <Button icon={<ArrowLeftOutlined />} onClick={() => setPage('home')}>返回首页</Button>
            </div>
            <DataEntry />
          </div>
        );
      default:
        return <HomePage onNavigate={setPage} />;
    }
  };

  return (
    <Layout className="layout">
      <Header style={{ background: '#1890ff', padding: '0 50px', display: 'flex', alignItems: 'center' }}>
        <div style={{ color: 'white', fontSize: 20, fontWeight: 'bold' }}>
          🎯 云志选
        </div>
        {page !== 'home' && (
          <Space style={{ marginLeft: 32 }}>
            <Button ghost size="small" onClick={() => setPage('query')}
              type={page === 'query' ? 'primary' : 'default'} ghost>
              数据查询
            </Button>
            <Button ghost size="small" onClick={() => setPage('simulator')}
              type={page === 'simulator' ? 'primary' : 'default'} ghost>
              志愿填报
            </Button>
            <Button ghost size="small" onClick={() => setPage('data-entry')}
              type={page === 'data-entry' ? 'primary' : 'default'} ghost>
              数据录入
            </Button>
          </Space>
        )}
      </Header>

      <Content style={{ padding: '40px 50px', minHeight: 'calc(100vh - 134px)' }}>
        {renderPage()}
      </Content>

      <Footer style={{ textAlign: 'center' }}>
        云志选 ©2026 Created for 云南高考考生
      </Footer>
    </Layout>
  );
}

export default App;

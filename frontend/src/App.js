import React, { useState } from 'react';
import { Layout, Menu, Card, Steps, message } from 'antd';
import { UserOutlined, UnorderedListOutlined, BarChartOutlined, FileTextOutlined } from '@ant-design/icons';
import StudentForm from './components/StudentForm';
import RecommendationList from './components/RecommendationList';
import VolunteerTable from './components/VolunteerTable';
import './App.css';

const { Header, Content, Footer } = Layout;
const { Step } = Steps;

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [studentInfo, setStudentInfo] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  const steps = [
    {
      title: '录入信息',
      icon: <UserOutlined />,
      content: <StudentForm onSubmit={handleStudentSubmit} />
    },
    {
      title: '智能推荐',
      icon: <BarChartOutlined />,
      content: <RecommendationList 
        recommendations={recommendations} 
        onGenerateVolunteerTable={handleGenerateTable}
      />
    },
    {
      title: '志愿方案',
      icon: <UnorderedListOutlined />,
      content: <VolunteerTable studentInfo={studentInfo} recommendations={recommendations} />
    },
    {
      title: '导出方案',
      icon: <FileTextOutlined />,
      content: <ExportPlan studentInfo={studentInfo} recommendations={recommendations} />
    }
  ];

  async function handleStudentSubmit(values) {
    try {
      // 调用后端API获取推荐
      const response = await fetch('http://localhost:8000/api/recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });
      
      const data = await response.json();
      setStudentInfo(values);
      setRecommendations(data);
      setCurrentStep(1);
      message.success('推荐生成成功！');
    } catch (error) {
      message.error('生成推荐失败：' + error.message);
    }
  }

  function handleGenerateTable() {
    setCurrentStep(2);
  }

  return (
    <Layout className="layout">
      <Header style={{ background: '#1890ff', padding: '0 50px' }}>
        <div className="logo" style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
          🎯 云志选 - 2026云南高考志愿决策系统
        </div>
      </Header>
      
      <Content style={{ padding: '50px 50px', minHeight: 'calc(100vh - 134px)' }}>
        <Card>
          <Steps current={currentStep} style={{ marginBottom: 40 }}>
            {steps.map(item => (
              <Step key={item.title} title={item.title} icon={item.icon} />
            ))}
          </Steps>
          
          <div className="steps-content" style={{ marginTop: 40 }}>
            {steps[currentStep].content}
          </div>
        </Card>
      </Content>
      
      <Footer style={{ textAlign: 'center' }}>
        云志选 ©2026 Created for 云南高考考生
      </Footer>
    </Layout>
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
        padding: '10px 30px',
        fontSize: '16px',
        background: '#1890ff',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer'
      }}>
        导出JSON文件
      </button>
    </div>
  );
}

export default App;

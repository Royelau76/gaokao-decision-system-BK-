import React from 'react';
import { Form, InputNumber, Select, Checkbox, Button, Row, Col, Card } from 'antd';

const { Option } = Select;

const StudentForm = ({ onSubmit }) => {
  const [form] = Form.useForm();

  const onFinish = (values) => {
    // 将分数转换为位次
    const rank = convertScoreToRank(values.score);
    const formData = {
      ...values,
      rank,
    };
    onSubmit(formData);
  };

  return (
    <Card title="📝 考生信息录入" bordered={false}>
      <Form
        form={form}
        name="studentForm"
        onFinish={onFinish}
        layout="vertical"
        initialValues={{
          subjects: ['物理', '化学', '生物'],
          risk_tolerance: '稳健'
        }}
      >
        <Row gutter={24}>
          <Col span={12}>
            <Form.Item
              name="score"
              label="高考总分"
              rules={[{ required: true, message: '请输入高考总分' }]}
            >
              <InputNumber 
                min={400} 
                max={750} 
                style={{ width: '100%' }} 
                placeholder="请输入分数"
              />
            </Form.Item>
          </Col>
          
          <Col span={12}>
            <Form.Item
              name="rank"
              label="全省位次（自动计算）"
            >
              <InputNumber 
                style={{ width: '100%' }} 
                disabled 
                placeholder="将根据分数自动计算"
              />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          name="subjects"
          label="选科组合"
          rules={[{ required: true, message: '请选择选科组合' }]}
        >
          <Checkbox.Group>
            <Row>
              <Col span={8}><Checkbox value="物理">物理</Checkbox></Col>
              <Col span={8}><Checkbox value="化学">化学</Checkbox></Col>
              <Col span={8}><Checkbox value="生物">生物</Checkbox></Col>
              <Col span={8}><Checkbox value="历史">历史</Checkbox></Col>
              <Col span={8}><Checkbox value="地理">地理</Checkbox></Col>
              <Col span={8}><Checkbox value="政治">政治</Checkbox></Col>
            </Row>
          </Checkbox.Group>
        </Form.Item>

        <Form.Item
          name="preference_region"
          label="偏好地区（可多选）"
        >
          <Select mode="multiple" placeholder="选择您偏好的地区">
            <Option value="北京">北京</Option>
            <Option value="上海">上海</Option>
            <Option value="江苏">江苏</Option>
            <Option value="浙江">浙江</Option>
            <Option value="广东">广东</Option>
            <Option value="四川">四川</Option>
            <Option value="陕西">陕西</Option>
            <Option value="湖北">湖北</Option>
            <Option value="其他">其他</Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="preference_major"
          label="偏好专业（可多选）"
        >
          <Select mode="multiple" placeholder="选择您偏好的专业类型">
            <Option value="计算机">计算机科学与技术</Option>
            <Option value="软件工程">软件工程</Option>
            <Option value="人工智能">人工智能</Option>
            <Option value="电子信息">电子信息工程</Option>
            <Option value="微电子">微电子科学与工程</Option>
            <Option value="自动化">自动化</Option>
            <Option value="数学">数学与应用数学</Option>
            <Option value="物理">物理学</Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="risk_tolerance"
          label="风险偏好"
          rules={[{ required: true }]}
        >
          <Select>
            <Option value="激进">激进 - 冲名校，接受调剂</Option>
            <Option value="稳健">稳健 - 平衡理想与稳妥</Option>
            <Option value="保守">保守 - 确保录取，不滑档</Option>
          </Select>
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" size="large" block>
            🚀 开始智能推荐
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

// 分数转位次函数（前端估算）
function convertScoreToRank(score) {
  const scoreRankMap = {
    683: 52,
    675: 95,
    670: 169,
    665: 268,
    660: 415,
    655: 619,
    650: 876,
    645: 1261,
    640: 1698,
    635: 2260,
    630: 2974,
    625: 3813,
    620: 4699,
    615: 4901,
  };
  
  const scores = Object.keys(scoreRankMap).map(Number).sort((a, b) => a - b);
  
  if (score >= Math.max(...scores)) return scoreRankMap[Math.max(...scores)];
  if (score <= Math.min(...scores)) return scoreRankMap[Math.min(...scores)];
  
  for (let i = 0; i < scores.length - 1; i++) {
    if (scores[i] <= score && score <= scores[i + 1]) {
      const x1 = scores[i];
      const y1 = scoreRankMap[x1];
      const x2 = scores[i + 1];
      const y2 = scoreRankMap[x2];
      return Math.round(y1 + (y2 - y1) * (score - x1) / (x2 - x1));
    }
  }
  
  return 5000;
}

export default StudentForm;

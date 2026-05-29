import React, { useState } from 'react';
import { Form, InputNumber, Select, Checkbox, Button, Row, Col, Card, message } from 'antd';

const { Option } = Select;

const LAYER1_CATEGORIES = [
  '计算机类', '电子信息类', '半导体类', '自动化类', '电气类',
  '机械类', '材料类', '能源动力类', '航空航天类', '土木类',
  '化学化工类', '交通运输类', '海洋类', '力学类',
  '数学类', '物理类', '生物类', '环境类', '天文地理类',
  '医学类', '经济管理类', '法学类', '心理学',
];

const StudentForm = ({ onSubmit }) => {
  const [form] = Form.useForm();
  const [computedRank, setComputedRank] = useState(null);
  const [yearUsed, setYearUsed] = useState(null);
  const [loading, setLoading] = useState(false);

  const recomputeRank = async (score, year) => {
    if (!score || score < 400) {
      setComputedRank(null);
      setYearUsed(null);
      return;
    }
    try {
      const url = year
        ? `/api/score-conversion?score=${score}&year=${year}`
        : `/api/score-conversion?score=${score}`;
      const resp = await fetch(url);
      const data = await resp.json();
      setComputedRank(data.estimated_rank);
      setYearUsed(data.year_used);
    } catch {
      setComputedRank(null);
      setYearUsed(null);
    }
  };

  const onScoreChange = (score) => {
    const year = form.getFieldValue('year');
    recomputeRank(score, year);
  };

  const onYearChange = (year) => {
    const score = form.getFieldValue('score');
    recomputeRank(score, year);
  };

  const onFinish = (values) => {
    const formData = {
      ...values,
      rank: computedRank || 5000,
    };
    onSubmit(formData);
  };

  return (
    <Card title="考生信息录入" bordered={false}>
      <Form
        form={form}
        name="studentForm"
        onFinish={onFinish}
        layout="vertical"
        initialValues={{
          subjects: ['物理', '化学', '生物'],
          risk_tolerance: '稳健',
          year: 2026
        }}
      >
        <Row gutter={24}>
          <Col xs={24} sm={12}>
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
                onChange={onScoreChange}
              />
            </Form.Item>
          </Col>

          <Col span={12}>
            <Form.Item label={yearUsed ? `全省位次（基于 ${yearUsed} 年一分一段表）` : '全省位次（自动计算）'}>
              <InputNumber
                style={{ width: '100%' }}
                value={computedRank}
                disabled
                placeholder="输入分数后自动计算"
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={24}>
          <Col xs={24} sm={12}>
            <Form.Item name="year" label="考生年份（决定一分一段表）" rules={[{ required: true }]}>
              <Select onChange={onYearChange}>
                <Option value={2024}>2024年</Option>
                <Option value={2025}>2025年</Option>
                <Option value={2026}>2026年</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
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
          </Col>
        </Row>

        <Form.Item
          name="subjects"
          label="选科组合"
          rules={[{ required: true, message: '请选择选科组合' }]}
        >
          <Checkbox.Group>
            <Row>
              <Col xs={8} sm={4}><Checkbox value="物理">物理</Checkbox></Col>
              <Col xs={8} sm={4}><Checkbox value="化学">化学</Checkbox></Col>
              <Col xs={8} sm={4}><Checkbox value="生物">生物</Checkbox></Col>
              <Col xs={8} sm={4}><Checkbox value="历史">历史</Checkbox></Col>
              <Col xs={8} sm={4}><Checkbox value="地理">地理</Checkbox></Col>
              <Col xs={8} sm={4}><Checkbox value="政治">政治</Checkbox></Col>
            </Row>
          </Checkbox.Group>
        </Form.Item>

        <Form.Item
          name="preference_region"
          label="偏好地区（可多选，留空表示不限）"
        >
          <Select mode="multiple" placeholder="选择您偏好的地区，留空表示不限" allowClear>
            <Option value="北京">北京</Option>
            <Option value="上海">上海</Option>
            <Option value="江苏">江苏</Option>
            <Option value="浙江">浙江</Option>
            <Option value="广东">广东</Option>
            <Option value="四川">四川</Option>
            <Option value="陕西">陕西</Option>
            <Option value="湖北">湖北</Option>
            <Option value="天津">天津</Option>
            <Option value="重庆">重庆</Option>
            <Option value="湖南">湖南</Option>
            <Option value="福建">福建</Option>
            <Option value="安徽">安徽</Option>
            <Option value="山东">山东</Option>
            <Option value="辽宁">辽宁</Option>
            <Option value="黑龙江">黑龙江</Option>
            <Option value="吉林">吉林</Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="preference_major"
          label="偏好专业大类（可多选，按 Layer 1 大类匹配）"
        >
          <Select mode="multiple" placeholder="选择您偏好的专业大类，留空表示不限" allowClear>
            {LAYER1_CATEGORIES.map(c => (
              <Option key={c} value={c}>{c}</Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" size="large" block loading={loading}>
            开始智能推荐
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default StudentForm;
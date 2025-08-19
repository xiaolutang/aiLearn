# Flutter Widget测试用例

## 1. 测试概述

### 1.1 测试目标
- 验证UI组件正确渲染
- 确保用户交互响应正常
- 验证状态管理正确性
- 确保组件间通信有效

### 1.2 测试框架
- **测试工具**：Flutter Test
- **测试类型**：Widget Test
- **断言库**：Flutter Test Matchers

## 2. 通用组件测试

### 2.1 自定义按钮组件测试

#### TC_W001: 自定义按钮渲染测试
- **测试目标**：验证自定义按钮正确渲染
- **前置条件**：无
- **测试步骤**：
  1. 创建CustomButton widget
  2. 设置按钮文本和样式
  3. 渲染组件
- **预期结果**：
  - 按钮正确显示
  - 文本内容正确
  - 样式符合设计规范

```dart
testWidgets('自定义按钮渲染测试', (WidgetTester tester) async {
  await tester.pumpWidget(
    MaterialApp(
      home: Scaffold(
        body: CustomButton(
          text: '测试按钮',
          onPressed: () {},
        ),
      ),
    ),
  );
  
  expect(find.text('测试按钮'), findsOneWidget);
  expect(find.byType(CustomButton), findsOneWidget);
});
```

#### TC_W002: 按钮点击事件测试
- **测试目标**：验证按钮点击事件正确触发
- **前置条件**：按钮已渲染
- **测试步骤**：
  1. 创建带回调的按钮
  2. 模拟点击事件
  3. 验证回调执行
- **预期结果**：点击回调正确执行

```dart
testWidgets('按钮点击事件测试', (WidgetTester tester) async {
  bool isPressed = false;
  
  await tester.pumpWidget(
    MaterialApp(
      home: Scaffold(
        body: CustomButton(
          text: '点击测试',
          onPressed: () {
            isPressed = true;
          },
        ),
      ),
    ),
  );
  
  await tester.tap(find.byType(CustomButton));
  expect(isPressed, isTrue);
});
```

### 2.2 输入框组件测试

#### TC_W003: 文本输入测试
- **测试目标**：验证文本输入功能
- **前置条件**：输入框已渲染
- **测试步骤**：
  1. 创建文本输入框
  2. 输入测试文本
  3. 验证输入内容
- **预期结果**：输入内容正确显示

```dart
testWidgets('文本输入测试', (WidgetTester tester) async {
  final controller = TextEditingController();
  
  await tester.pumpWidget(
    MaterialApp(
      home: Scaffold(
        body: TextField(
          controller: controller,
          key: const Key('test_input'),
        ),
      ),
    ),
  );
  
  await tester.enterText(find.byKey(const Key('test_input')), '测试输入');
  expect(controller.text, '测试输入');
});
```

#### TC_W004: 输入验证测试
- **测试目标**：验证输入验证功能
- **前置条件**：带验证的输入框已渲染
- **测试步骤**：
  1. 输入无效内容
  2. 触发验证
  3. 验证错误提示
- **预期结果**：显示正确的错误提示

## 3. 页面级组件测试

### 3.1 登录页面测试

#### TC_W005: 登录页面渲染测试
- **测试目标**：验证登录页面正确渲染
- **前置条件**：无
- **测试步骤**：
  1. 导航到登录页面
  2. 验证页面元素
- **预期结果**：
  - 用户名输入框存在
  - 密码输入框存在
  - 登录按钮存在
  - 页面标题正确

```dart
testWidgets('登录页面渲染测试', (WidgetTester tester) async {
  await tester.pumpWidget(
    MaterialApp(
      home: LoginPage(),
    ),
  );
  
  expect(find.text('用户登录'), findsOneWidget);
  expect(find.byKey(const Key('username_field')), findsOneWidget);
  expect(find.byKey(const Key('password_field')), findsOneWidget);
  expect(find.byKey(const Key('login_button')), findsOneWidget);
});
```

#### TC_W006: 登录表单验证测试
- **测试目标**：验证登录表单验证逻辑
- **前置条件**：登录页面已加载
- **测试步骤**：
  1. 不输入任何内容点击登录
  2. 验证错误提示
  3. 输入有效内容
  4. 验证验证通过
- **预期结果**：表单验证正确工作

### 3.2 成绩管理页面测试

#### TC_W007: 成绩列表渲染测试
- **测试目标**：验证成绩列表正确渲染
- **前置条件**：有测试数据
- **测试步骤**：
  1. 加载成绩管理页面
  2. 验证列表项显示
- **预期结果**：成绩列表正确显示

```dart
testWidgets('成绩列表渲染测试', (WidgetTester tester) async {
  final mockGrades = [
    Grade(studentName: '张三', subject: '数学', score: 95),
    Grade(studentName: '李四', subject: '语文', score: 88),
  ];
  
  await tester.pumpWidget(
    MaterialApp(
      home: GradesPage(grades: mockGrades),
    ),
  );
  
  expect(find.text('张三'), findsOneWidget);
  expect(find.text('李四'), findsOneWidget);
  expect(find.text('95'), findsOneWidget);
  expect(find.text('88'), findsOneWidget);
});
```

#### TC_W008: 成绩图表渲染测试
- **测试目标**：验证成绩图表正确渲染
- **前置条件**：有图表数据
- **测试步骤**：
  1. 加载包含图表的页面
  2. 验证图表组件存在
- **预期结果**：图表正确显示

### 3.3 学生管理页面测试

#### TC_W009: 学生列表测试
- **测试目标**：验证学生列表功能
- **前置条件**：有学生数据
- **测试步骤**：
  1. 加载学生管理页面
  2. 验证学生信息显示
  3. 测试搜索功能
- **预期结果**：学生列表和搜索功能正常

#### TC_W010: 添加学生测试
- **测试目标**：验证添加学生功能
- **前置条件**：在学生管理页面
- **测试步骤**：
  1. 点击添加按钮
  2. 填写学生信息
  3. 提交表单
- **预期结果**：学生成功添加到列表

## 4. 导航和路由测试

### 4.1 底部导航测试

#### TC_W011: 底部导航切换测试
- **测试目标**：验证底部导航切换功能
- **前置条件**：应用已启动
- **测试步骤**：
  1. 点击不同的导航标签
  2. 验证页面切换
- **预期结果**：页面正确切换

```dart
testWidgets('底部导航切换测试', (WidgetTester tester) async {
  await tester.pumpWidget(MyApp());
  
  // 点击成绩管理标签
  await tester.tap(find.text('成绩管理'));
  await tester.pumpAndSettle();
  
  expect(find.byType(GradesPage), findsOneWidget);
  
  // 点击学生管理标签
  await tester.tap(find.text('学生管理'));
  await tester.pumpAndSettle();
  
  expect(find.byType(StudentsPage), findsOneWidget);
});
```

### 4.2 页面路由测试

#### TC_W012: 页面跳转测试
- **测试目标**：验证页面间跳转功能
- **前置条件**：在主页面
- **测试步骤**：
  1. 点击跳转按钮
  2. 验证目标页面加载
  3. 测试返回功能
- **预期结果**：页面跳转和返回正常

## 5. 状态管理测试

### 5.1 Provider状态测试

#### TC_W013: 状态更新测试
- **测试目标**：验证Provider状态更新
- **前置条件**：使用Provider的组件
- **测试步骤**：
  1. 触发状态更新操作
  2. 验证UI更新
- **预期结果**：UI正确反映状态变化

```dart
testWidgets('状态更新测试', (WidgetTester tester) async {
  await tester.pumpWidget(
    ChangeNotifierProvider(
      create: (_) => GradesProvider(),
      child: MaterialApp(
        home: GradesPage(),
      ),
    ),
  );
  
  // 触发状态更新
  await tester.tap(find.byKey(const Key('refresh_button')));
  await tester.pump();
  
  // 验证UI更新
  expect(find.byType(CircularProgressIndicator), findsOneWidget);
});
```

## 6. 响应式设计测试

### 6.1 屏幕尺寸适配测试

#### TC_W014: 不同屏幕尺寸测试
- **测试目标**：验证不同屏幕尺寸下的布局
- **前置条件**：响应式组件
- **测试步骤**：
  1. 设置不同的屏幕尺寸
  2. 验证布局适配
- **预期结果**：布局在不同尺寸下正确显示

```dart
testWidgets('屏幕尺寸适配测试', (WidgetTester tester) async {
  // 测试手机尺寸
  await tester.binding.setSurfaceSize(const Size(375, 667));
  await tester.pumpWidget(MaterialApp(home: ResponsivePage()));
  
  expect(find.byKey(const Key('mobile_layout')), findsOneWidget);
  
  // 测试平板尺寸
  await tester.binding.setSurfaceSize(const Size(768, 1024));
  await tester.pump();
  
  expect(find.byKey(const Key('tablet_layout')), findsOneWidget);
});
```

## 7. 性能相关测试

### 7.1 渲染性能测试

#### TC_W015: 大列表渲染测试
- **测试目标**：验证大列表渲染性能
- **前置条件**：大量数据
- **测试步骤**：
  1. 加载包含大量数据的列表
  2. 测试滚动性能
- **预期结果**：列表滚动流畅

## 8. 错误处理测试

### 8.1 异常情况测试

#### TC_W016: 网络错误处理测试
- **测试目标**：验证网络错误时的UI表现
- **前置条件**：模拟网络错误
- **测试步骤**：
  1. 触发网络请求
  2. 模拟网络错误
  3. 验证错误提示
- **预期结果**：显示友好的错误提示

## 9. 测试执行指南

### 9.1 测试环境准备
```bash
# 安装依赖
flutter pub get

# 运行所有Widget测试
flutter test

# 运行特定测试文件
flutter test test/widget/login_test.dart

# 生成测试覆盖率报告
flutter test --coverage
genhtml coverage/lcov.info -o coverage/html
```

### 9.2 测试最佳实践
1. **测试隔离**：每个测试用例独立运行
2. **数据准备**：使用Mock数据避免外部依赖
3. **异步处理**：正确处理异步操作
4. **清理资源**：测试后清理状态和资源
5. **描述清晰**：测试名称和描述要清晰明确

### 9.3 常用测试工具
- **find.byType()**: 按组件类型查找
- **find.byKey()**: 按Key查找
- **find.text()**: 按文本查找
- **tester.tap()**: 模拟点击
- **tester.enterText()**: 模拟文本输入
- **tester.pump()**: 触发重建
- **tester.pumpAndSettle()**: 等待动画完成

---

**文档版本**：1.0  
**创建日期**：2024年1月  
**测试框架**：Flutter Test  
**覆盖范围**：UI组件、交互、状态管理
export const categories = [
  { id: 'all', name: '全部漏洞', count: 0 },
  { id: 'sqli', name: 'SQL注入', count: 3 },
  { id: 'xss', name: 'XSS攻击', count: 3 },
  { id: 'csrf', name: 'CSRF攻击', count: 1 },
  { id: 'deserialization', name: '反序列化', count: 2 },
  { id: 'upload', name: '文件上传', count: 1 }
]

export const vulnerabilities = [
  {
    id: 1,
    name: 'SQL注入-初级',
    category: 'sqli',
    difficulty: 'easy',
    summary: '简单的SQL注入入门，学习基本绕过登录',
    tags: ['入门', '登录绕过'],
    description: 'SQL注入（SQL Injection）是一种常见的Web安全漏洞，攻击者通过在输入框中注入恶意的SQL代码，来操纵后端数据库执行未授权的操作。这是最严重的漏洞之一，可能导致数据泄露、数据篡改、服务器控制等严重后果。',
    impact: [
      '数据泄露：攻击者可以读取敏感数据（用户信息、密码等）',
      '数据篡改：修改数据库中的数据',
      '数据删除：删除重要数据',
      '服务器控制：获取服务器控制权'
    ],
    principle: '<p>当应用程序直接将用户输入拼接到SQL查询语句中时，就会产生SQL注入漏洞。例如：</p><pre><code>username = GET["username"]\nsql = "SELECT * FROM users WHERE username = \'" + username + "\'"</code></pre><p>如果用户输入 <code>\' OR 1=1 --</code>，SQL就会变成：</p><pre><code>SELECT * FROM users WHERE username = \'\' OR 1=1 --\'</code></pre><p>这时1=1永远为真，查询会返回所有用户记录。</p>',
    defense: [
      '使用参数化查询（Prepared Statements）',
      '使用ORM框架',
      '对用户输入进行严格的验证和过滤',
      '最小权限原则：数据库用户权限最小化',
      '使用WAF（Web应用防火墙）'
    ],
    codeExample: `// 错误写法 - 直接拼接
$username = $_POST['username'];
$sql = "SELECT * FROM users WHERE username = '$username'";

// 正确写法 - 参数化查询
$stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
$stmt->execute([$username]);

// 正确写法 - 使用ORM
$user = User::where('username', $username)->first();`,
    flowDiagram: [
      { title: '用户输入', description: '用户在表单中输入恶意SQL语句' },
      { title: 'SQL拼接', description: '后端将用户输入直接拼接到SQL语句中' },
      { title: '数据库执行', description: '数据库执行了被篡改的SQL' },
      { title: '绕过验证', description: '恶意SQL使条件永真，成功绕过' },
      { title: '获取数据', description: '攻击者成功获取敏感数据' }
    ],
    vulnCode: `// 有漏洞的代码
username = request.form['username']
password = request.form['password']

sql = f"""SELECT * FROM users
         WHERE username = '{username}'
         AND password = '{password}'"""

result = db.execute(sql)`,
    secureCode: `// 安全的代码
username = request.form['username']
password = request.form['password']

// 使用参数化查询
sql = """SELECT * FROM users
         WHERE username = ?
         AND password = ?"""

result = db.execute(
    sql,
    (username, password)
)`,
    checklist: [
      '使用参数化查询代替字符串拼接',
      '验证用户输入的类型和长度',
      '数据库用户使用最小权限',
      '配置Web应用防火墙',
      '定期审计代码中的SQL查询',
      '使用ORM框架'
    ]
  },
  {
    id: 2,
    name: 'SQL注入-中级',
    category: 'sqli',
    difficulty: 'medium',
    summary: '学习绕过简单过滤的SQL注入技巧',
    tags: ['中级', '绕过WAF'],
    description: '中级SQL注入需要绕过一些基本的过滤，比如注释符过滤、关键字过滤等。这时候需要学习更复杂的注入技巧。',
    impact: [
      '绕过滤后可以进行更深入的注入',
      '获取更多敏感数据',
      '甚至可以写文件或执行命令'
    ],
    principle: '<p>当应用程序过滤了常见的SQL注入关键词时，可以通过各种绕过技巧继续注入：</p><ul><li>大小写绕过：SELECT → sElEcT</li><li>注释替换：空格 → /**/</li><li>双写绕过：UNION → UNUNIONION</li><li>编码绕过：URL编码、十六进制</li></ul>',
    defense: [
      '使用白名单而非黑名单',
      '使用预编译语句',
      '配置更严格的WAF规则',
      '输入长度限制'
    ],
    codeExample: `// 被过滤的写法
'union select 1,2,3 --

// 绕过技巧
'UN/**/ION SEL/**/ECT 1,2,3
'sElEcT 1,2,3
'ununionion selselectect 1,2,3`,
    flowDiagram: [
      { title: '检测过滤', description: '先测试哪些关键词被过滤' },
      { title: '寻找绕过', description: '尝试各种绕过技巧' },
      { title: '成功注入', description: '使用合适的方法绕过' },
      { title: '获取数据', description: '通过盲注等方法提取数据' }
    ],
    vulnCode: `// 简单过滤无效
username = request.form['username']
// 只过滤了UNION
username = username.replace('UNION', '')
// 但双写可以绕过：UNUNIONION -> UNION`,
    secureCode: `// 使用参数化查询
stmt = db.prepare("SELECT * FROM users WHERE id = ?")
stmt.execute([user_id])`,
    checklist: [
      '不依赖黑名单过滤',
      '使用参数化查询',
      '配置WAF检测异常SQL',
      '限制输入长度'
    ]
  },
  {
    id: 3,
    name: '反射型XSS',
    category: 'xss',
    difficulty: 'easy',
    summary: '学习基础的反射型跨站脚本攻击',
    tags: ['入门', 'XSS'],
    description: '反射型XSS（Reflected XSS）是最常见的XSS类型，恶意脚本不会存储在服务器上，而是通过URL参数反射到页面上。',
    impact: [
      '窃取用户Cookie和会话',
      '伪造用户操作',
      '钓鱼攻击',
      '重定向到恶意网站'
    ],
    principle: '<p>当应用程序将URL参数直接输出到HTML页面中时，就产生了反射型XSS：</p><pre><code>// 搜索参数直接输出\nsearch = request.GET["q"]\necho "<h1>搜索结果: " + search + "</h1>"</code></pre><p>用户访问 <code>?q=&lt;script&gt;alert(1)&lt;/script&gt;</code> 时，脚本就会执行。</p>',
    defense: [
      '对输出进行HTML转义',
      '使用Content Security Policy (CSP)',
      '使用HttpOnly cookie',
      '输入验证和过滤'
    ],
    codeExample: `// 有漏洞的代码
search = req.query.search;
res.send(\`<div>搜索: \${search}</div>\`);

// 安全的代码
search = escapeHTML(req.query.search);
res.send(\`<div>搜索: \${search}</div>\`);

// 使用框架自动转义
res.render('search', { search: req.query.search });`,
    flowDiagram: [
      { title: '构造恶意URL', description: '攻击者构造包含XSS的URL' },
      { title: '发送给用户', description: '通过邮件/聊天发送恶意链接' },
      { title: '用户点击', description: '用户点击链接访问' },
      { title: '脚本执行', description: '页面渲染时执行恶意脚本' },
      { title: '数据泄露', description: 'Cookie等敏感信息被盗取' }
    ],
    vulnCode: `// 直接输出用户输入
<%
  String name = request.getParameter("name");
  out.println("Hello, " + name);
%>

// 访问 ?name=<scr" + "ipt>steal()</scr" + "ipt>`,
    secureCode: `// HTML转义输出
<%
  String name = request.getParameter("name");
  out.println("Hello, " + escapeHtml(name));
%>

// 或使用JSTL自动转义
<c:out value="\\${name}" />`,
    checklist: [
      '所有输出到HTML的内容都要转义',
      '设置HttpOnly标记防止Cookie窃取',
      '配置CSP策略',
      '避免使用innerHTML插入用户输入'
    ]
  },
  {
    id: 4,
    name: '存储型XSS',
    category: 'xss',
    difficulty: 'hard',
    summary: '存储型XSS是最危险的XSS类型',
    tags: ['危险', '持久化'],
    description: '存储型XSS（Stored XSS）的恶意代码会存储在数据库中，每当有用户访问受影响的页面时，脚本都会执行。',
    impact: [
      '影响所有访问的用户',
      '持久化存在',
      '大规模攻击',
      '难以彻底清除'
    ],
    principle: '<p>当用户提交的内容被存储到数据库，然后在页面上展示时没有转义：</p><pre><code>// 用户提交评论\ncomment = request.form["comment"]\ndb.save(comment)\n\n// 其他用户查看\necho "<div>" + comment + "</div>"</code></pre><p>如果评论包含<scr" + "ipt>alert(1)</scr" + "ipt>，所有访问的用户都会受影响。</p>',
    defense: [
      '输入时进行严格验证',
      '输出时进行完整HTML转义',
      '使用富文本编辑器时使用白名单',
      '配置严格的CSP'
    ],
    codeExample: `// 存储后直接输出
comment = request.form.comment
db.comments.insertOne({ text: comment })

// 输出时
for (const c of comments) {
  document.getElementById('comments').innerHTML +=
    '<div>' + c.text + '</div>';
}

// 安全处理
function sanitizeHTML(str) {
  return str.replace(/[&<>"]/g, m => ({
    '&': '&amp;', '<': '&lt;',
    '>': '&gt;', '"': '&quot;'
  })[m])
}

// 输出时转义
innerHTML = sanitizeHTML(c.text);`,
    flowDiagram: [
      { title: '提交恶意内容', description: '攻击者在表单提交XSS payload' },
      { title: '存储到数据库', description: '恶意内容保存到数据库' },
      { title: '用户访问', description: '其他用户访问包含内容的页面' },
      { title: '脚本自动执行', description: '页面加载时XSS自动执行' },
      { title: '大规模感染', description: '所有访问用户都受影响' }
    ],
    vulnCode: `// 直接保存和输出
post = request.body.post
Post.create({ content: post })

// 直接输出
res.send(post.content)`,
    secureCode: `// 存储前验证 + 输出时转义
post = sanitizeHTML(request.body.post)
Post.create({ content: post })

// 使用DOMPurify库
post = DOMPurify.sanitize(request.body.post)`,
    checklist: [
      '用户生成内容必须严格过滤',
      '输出时转义是最后防线',
      '使用DOMPurify等专业库',
      'CSP禁止内联脚本'
    ]
  },
  {
    id: 5,
    name: '文件上传漏洞',
    category: 'upload',
    difficulty: 'medium',
    summary: '学习绕过文件上传限制的方法',
    tags: ['上传', 'Webshell'],
    description: '文件上传漏洞允许攻击者上传任意文件，最常见的是上传脚本文件（如.php、.jsp）并获取服务器执行权限。',
    impact: [
      '上传Webshell获取服务器权限',
      '上传恶意HTML进行XSS',
      '上传病毒/后门程序',
      '覆盖重要文件'
    ],
    principle: '<p>当文件上传功能验证不严格时，攻击者可以：</p><ul><li>更改扩展名绕过：.php → .php5</li><li>双扩展名：.php.jpg</li><li>Content-Type伪造</li><li>文件内容伪造</li></ul>',
    defense: [
      '白名单验证文件扩展名',
      '验证文件内容类型',
      '重命名文件',
      '禁止上传目录执行权限',
      '文件上传到非Web可访问目录'
    ],
    codeExample: `// 简单扩展名检查
ext = file.filename.split('.').pop()
if ext not in ['jpg', 'png', 'gif']:
    return 'Invalid file'
// 可以用 .php.jpg 或 .php5 绕过

// 严格验证
ALLOWED_EXT = {'jpg', 'png', 'gif'}
ALLOWED_MIME = {'image/jpeg', 'image/png'}
ext = file.filename.split('.').pop().lower()
if ext not in ALLOWED_EXT:
    return 'Invalid'
if file.mime not in ALLOWED_MIME:
    return 'Invalid'
// 重命名
new_name = uuid.uuid4().hex + '.' + ext
save_to = '/uploads/' + new_name
// 设置权限
os.chmod(save_to, 0o644)`,
    flowDiagram: [
      { title: '上传Webshell', description: '构造恶意文件绕过验证' },
      { title: '上传成功', description: '服务器保存恶意文件' },
      { title: '访问执行', description: '通过URL访问执行脚本' },
      { title: '获取Shell', description: '成功获得服务器控制权' }
    ],
    vulnCode: `// 只检查扩展名
file = req.files.upload
ext = path.extname(file.name)
if ext === '.php' { throw 'Invalid' }

// 多重验证
if (!isImage(file.data)) { throw 'Not image' }
safeName = uuid() + '.jpg'
file.mv('/uploads/' + safeName)`,
    checklist: [
      '验证文件扩展名白名单',
      '验证文件内容格式',
      '重命名上传文件',
      '上传目录无执行权限',
      '文件存储在Web根以外'
    ]
  },
  {
    id: 6,
    name: 'PHP反序列化',
    category: 'deserialization',
    difficulty: 'hard',
    summary: '反序列化漏洞可导致远程代码执行',
    tags: ['RCE', '危险'],
    description: 'PHP反序列化漏洞允许攻击者通过构造恶意的序列化字符串，在unserialize()时执行危险代码，导致远程代码执行。',
    impact: [
      '远程代码执行 (RCE)',
      '任意文件读写',
      '服务器控制',
      '权限提升'
    ],
    principle: '<p>当类存在__destruct()或__wakeup()等魔术方法时：</p><pre><code>class User {\n  function __destruct() {\n    unlink(\$this->file);\n  }\n}\nunserialize(\$_GET[\'data\']);</code></pre><p>攻击者可以构造恶意对象删除任意文件。</p>',
    defense: [
      '禁止反序列化不可信数据',
      '使用JSON代替serialize',
      '升级PHP版本',
      '禁用危险函数'
    ],
    codeExample: `// 直接反序列化用户输入
$data = \$_GET['data'];
\$obj = unserialize(\$data);

// 使用JSON
\$data = \$_GET['data'];
\$obj = json_decode(\$data);
// 仅访问预期字段
if (property_exists(\$obj, 'name')) {
  \$name = \$obj->name;
}`,
    flowDiagram: [
      { title: '代码审计', description: '寻找unserialize点和危险类' },
      { title: '构造POC', description: '构造恶意序列化字符串' },
      { title: '触发执行', description: '反序列化时执行魔术方法' },
      { title: 'RCE成功', description: '获得代码执行能力' }
    ],
    vulnCode: `// 不安全的反序列化
\$userData = \$_COOKIE['user'];
\$user = unserialize(\$userData);

// 避免反序列化
\$userData = \$_COOKIE['user'];
\$user = json_decode(\$userData);`,
    checklist: [
      '避免反序列化用户输入',
      '使用JSON/XML等数据格式',
      '禁用危险魔术方法',
      '升级PHP版本'
    ]
  }
]

export const difficultyLabels = {
  easy: '简单',
  medium: '中等',
  hard: '困难'
}

export const difficultyColors = {
  easy: { bg: '#dcfce7', text: '#166534', border: '#22c55e' },
  medium: { bg: '#fef3c7', text: '#92400e', border: '#f59e0b' },
  hard: { bg: '#fee2e2', text: '#991b1b', border: '#ef4444' }
}

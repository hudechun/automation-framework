# 用户建议分析

## 一、用户建议的流程

### 1.1 用户建议

```
1. 上传格式文件，读取整个指令系统（简单明了）
   - 指令系统预先设置好的，也可以动态更新的
   
2. 把文档和指令系统给AI模型
   - 第一步：生成自然语言的格式要求
   - 第二步：按指令系统的格式，生成这个学校的子集指令系统
   
3. 把格式要求的自然语言和本校的子指令集传回本地，进行校验
   - 如何校验？
   - 校验通过，保存子集指令到数据库
```

---

## 二、与当前实现的对比

### 2.1 当前实现流程

```
1. 上传Word模板
   ↓
2. python-docx读取Word文档
   ↓
3. 提取文档格式信息（Python字典）
   ↓
4. 构建AI提示词（将字典转换为JSON字符串）
   ↓
5. AI分析格式信息并生成格式化指令
   - 一次生成：自然语言描述 + JSON格式指令
   ↓
6. 验证和修正格式指令
   ↓
7. 保存格式指令到数据库
```

---

### 2.2 用户建议的流程

```
1. 上传格式文件，读取整个指令系统
   - 指令系统：预先设置好的完整指令系统（通用格式）
   - 可以动态更新
   ↓
2. 把文档和指令系统给AI模型
   ↓
3. AI第一步：生成自然语言的格式要求
   ↓
4. AI第二步：按指令系统的格式，生成这个学校的子集指令系统
   ↓
5. 校验（自然语言 + 子指令集）
   ↓
6. 校验通过，保存子集指令到数据库
```

---

## 三、关键区别分析

### 3.1 指令系统的概念

**用户建议**：
- 有一个"完整的指令系统"（预先设置好的，通用格式）
- 每个学校使用"子集指令系统"（从完整指令系统中选择）

**当前实现**：
- 没有预先设置的完整指令系统
- 每次上传模板时，AI从零开始生成格式化指令

**优势**：
- ✅ 用户建议更符合"通用格式指令系统"的设计原则
- ✅ 有完整的指令系统作为模板，AI更容易生成准确的子集
- ✅ 可以动态更新完整指令系统，适应新的格式要求

---

### 3.2 AI生成方式

**用户建议**：
- 分两步生成：
  1. 第一步：生成自然语言的格式要求
  2. 第二步：按指令系统的格式，生成子集指令系统

**当前实现**：
- 一次生成：自然语言描述 + JSON格式指令

**优势**：
- ✅ 分两步生成，可以更好地控制生成过程
- ✅ 第一步生成自然语言，可以验证AI是否正确理解了格式要求
- ✅ 第二步生成子集指令系统，可以确保格式符合指令系统规范

---

### 3.3 校验方式

**用户建议**：
- 校验自然语言 + 子指令集
- 如何校验？（需要明确）

**当前实现**：
- 只校验JSON格式指令（检查异常值）

**优势**：
- ✅ 同时校验自然语言和子指令集，更全面
- ✅ 可以验证自然语言描述是否与子指令集一致

---

## 四、用户建议的优势

### ✅ 1. 更符合设计原则

**优势**：
- 有完整的指令系统作为模板
- 每个学校使用子集指令系统
- 符合"通用格式指令系统"的设计原则

---

### ✅ 2. 更可控的生成过程

**优势**：
- 分两步生成，可以更好地控制
- 第一步验证AI是否正确理解格式要求
- 第二步确保格式符合指令系统规范

---

### ✅ 3. 更全面的校验

**优势**：
- 同时校验自然语言和子指令集
- 可以验证一致性

---

## 五、实现建议

### 5.1 完整指令系统的设计

**建议**：
```json
{
  "version": "1.0",
  "description": "通用格式指令系统（所有可能的格式要求）",
  "instruction_type": "universal_format",
  "format_rules": {
    "default_font": {
      "name": "可选值列表：['宋体', '楷体_GB2312', '黑体', 'Times New Roman', ...]",
      "size_pt": "范围：8-30磅",
      "color": "RGB值"
    },
    "headings": {
      "h1": {
        "font_name": "可选值列表",
        "font_size_pt": "范围：8-30磅",
        "bold": "true/false",
        "alignment": "['left', 'center', 'right']",
        ...
      }
    },
    ...
  },
  "application_rules": {
    "chapter_numbering_format": {
      "level_1": {
        "format_type": "['chinese_chapter', 'numbered', 'roman']",
        "pattern": "格式模板",
        "number_style": "['chinese', 'arabic', 'roman']",
        ...
      }
    },
    "special_section_format_rules": {
      "abstract": {
        "title": "可选值：['摘要', 'Abstract', ...]",
        "should_have_numbering": "true/false",
        "position": "['after_toc', 'after_title', 'before_body']",
        ...
      }
    }
  }
}
```

**存储方式**：
- 可以存储在配置文件中
- 可以存储在数据库中
- 可以动态更新

---

### 5.2 AI生成流程

**建议**：
```python
# 第一步：生成自然语言的格式要求
natural_language_prompt = f"""
你是文档格式分析专家。

## 完整指令系统：
{universal_instruction_system}

## Word文档格式信息：
{document_content_json}

## 任务：
分析Word文档格式，生成自然语言的格式要求描述。
描述应该包括：
- 正文格式（字体、字号、行距等）
- 标题格式（各级标题的格式）
- 页面设置（页边距、纸张大小等）
- 特殊格式（目录、摘要、关键词等）
"""

natural_language_response = await ai.chat(natural_language_prompt)

# 第二步：生成子集指令系统
subset_instruction_prompt = f"""
你是文档格式分析专家。

## 完整指令系统：
{universal_instruction_system}

## Word文档格式信息：
{document_content_json}

## 自然语言格式要求：
{natural_language_response}

## 任务：
根据自然语言格式要求，从完整指令系统中选择相应的配置项，生成这个学校的子集指令系统。

要求：
1. 子集指令系统必须符合完整指令系统的格式规范
2. 只包含这个学校实际使用的格式配置
3. 所有值必须从Word文档中实际提取
"""

subset_instruction_response = await ai.chat(subset_instruction_prompt)
```

---

### 5.3 校验方式

**建议**：

#### 校验1：格式规范校验
```python
def validate_subset_instruction(subset_instruction, universal_instruction_system):
    """
    校验子集指令系统是否符合完整指令系统的格式规范
    """
    # 1. 检查JSON结构是否符合规范
    # 2. 检查所有字段是否在完整指令系统的可选值范围内
    # 3. 检查数值是否在合理范围内（如字体大小8-30磅）
    # 4. 检查必填字段是否存在
    pass
```

#### 校验2：一致性校验
```python
def validate_consistency(natural_language, subset_instruction):
    """
    校验自然语言描述与子集指令系统是否一致
    """
    # 1. 检查自然语言中提到的格式要求是否在子集指令系统中
    # 2. 检查子集指令系统中的配置是否在自然语言中有描述
    # 3. 检查关键格式（如字体大小）是否一致
    pass
```

#### 校验3：数据质量校验
```python
def validate_data_quality(subset_instruction):
    """
    校验子集指令系统的数据质量
    """
    # 1. 检查字体大小是否在合理范围内（8-30磅）
    # 2. 检查行距是否在合理范围内（0.5-3.0倍）
    # 3. 检查缩进是否为负数
    # 4. 自动修正异常值
    pass
```

---

## 六、实现方案

### 6.1 完整指令系统的存储

**方案1：存储在配置文件中**
```python
# config/universal_instruction_system.json
{
  "version": "1.0",
  "description": "通用格式指令系统",
  ...
}
```

**方案2：存储在数据库中**
```python
# 表：universal_instruction_system
# 字段：instruction_data (JSON)
```

**方案3：动态更新**
```python
# 可以通过API更新完整指令系统
# 可以版本化管理
```

---

### 6.2 AI生成流程的实现

**修改位置**：`format_service.py` 的 `_analyze_format_with_ai()` 方法

**实现**：
```python
async def _analyze_format_with_ai(
    cls,
    query_db: AsyncSession,
    document_content: Dict[str, Any],
    config_id: Optional[int] = None
) -> Dict[str, str]:
    # 1. 读取完整指令系统
    universal_instruction_system = await cls._get_universal_instruction_system(query_db)
    
    # 2. 第一步：生成自然语言的格式要求
    natural_language = await cls._generate_natural_language_format_requirement(
        query_db,
        document_content,
        universal_instruction_system,
        config_id
    )
    
    # 3. 第二步：生成子集指令系统
    subset_instruction = await cls._generate_subset_instruction_system(
        query_db,
        document_content,
        natural_language,
        universal_instruction_system,
        config_id
    )
    
    # 4. 校验
    validation_result = cls._validate_instruction_system(
        natural_language,
        subset_instruction,
        universal_instruction_system
    )
    
    if not validation_result['valid']:
        raise ServiceException(message=f"格式指令校验失败: {validation_result['errors']}")
    
    return {
        'natural_language_description': natural_language,
        'json_instructions': json.dumps(subset_instruction, ensure_ascii=False, indent=2)
    }
```

---

### 6.3 校验的实现

**修改位置**：`format_service.py` 添加新的校验方法

**实现**：
```python
@classmethod
def _validate_instruction_system(
    cls,
    natural_language: str,
    subset_instruction: Dict[str, Any],
    universal_instruction_system: Dict[str, Any]
) -> Dict[str, Any]:
    """
    校验子集指令系统
    
    :param natural_language: 自然语言格式要求
    :param subset_instruction: 子集指令系统
    :param universal_instruction_system: 完整指令系统
    :return: 校验结果
    """
    errors = []
    
    # 1. 格式规范校验
    format_errors = cls._validate_format_specification(
        subset_instruction,
        universal_instruction_system
    )
    errors.extend(format_errors)
    
    # 2. 一致性校验
    consistency_errors = cls._validate_consistency(
        natural_language,
        subset_instruction
    )
    errors.extend(consistency_errors)
    
    # 3. 数据质量校验
    quality_errors = cls._validate_data_quality(subset_instruction)
    errors.extend(quality_errors)
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }
```

---

## 七、优势总结

### ✅ 1. 更符合设计原则

- 有完整的指令系统作为模板
- 每个学校使用子集指令系统
- 符合"通用格式指令系统"的设计原则

---

### ✅ 2. 更可控的生成过程

- 分两步生成，可以更好地控制
- 第一步验证AI是否正确理解格式要求
- 第二步确保格式符合指令系统规范

---

### ✅ 3. 更全面的校验

- 同时校验自然语言和子指令集
- 可以验证一致性
- 可以验证格式规范

---

### ✅ 4. 更容易维护

- 完整指令系统可以动态更新
- 不需要修改代码，只需要更新指令系统
- 可以版本化管理

---

## 八、需要明确的问题

### 问题1：完整指令系统的来源

**问题**：
- 完整指令系统从哪里来？
- 如何初始化？
- 如何动态更新？

**建议**：
- 可以预先设计一个完整的指令系统模板
- 存储在配置文件或数据库中
- 可以通过API动态更新

---

### 问题2：校验的具体方式

**问题**：
- 如何校验自然语言和子指令集的一致性？
- 如何校验子集指令系统是否符合完整指令系统的格式规范？

**建议**：
- 格式规范校验：检查JSON结构、字段范围、数值范围
- 一致性校验：检查自然语言中提到的格式要求是否在子指令集中
- 数据质量校验：检查异常值，自动修正

---

### 问题3：两步生成的必要性

**问题**：
- 是否必须分两步生成？
- 是否可以合并为一步？

**建议**：
- 分两步生成可以更好地控制生成过程
- 第一步验证AI是否正确理解格式要求
- 第二步确保格式符合指令系统规范
- 但也可以考虑合并为一步，如果AI能力足够强

---

## 九、结论

**用户建议的优势**：
1. ✅ 更符合"通用格式指令系统"的设计原则
2. ✅ 更可控的生成过程
3. ✅ 更全面的校验
4. ✅ 更容易维护

**实现建议**：
1. ✅ 设计完整指令系统（存储在配置文件或数据库中）
2. ✅ 修改AI生成流程（分两步生成）
3. ✅ 实现校验逻辑（格式规范、一致性、数据质量）

**需要明确的问题**：
1. 完整指令系统的来源和更新方式
2. 校验的具体实现方式
3. 两步生成的必要性

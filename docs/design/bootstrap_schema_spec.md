# Feature: Bootstrap 元模型 Schema 设计 (Revised v2)

## 1. Context

Ref: `docs/architecture/bootstrap_standard.md`

本设计文档详细定义了 Bootstrap 相关的元模型结构（Schema），重点支持配置的统一规范定义和容器的层级化描述。

## 2. Schema Definitions

我们需要在 `DomainDefinition` 上下文中新增和修改一系列 Value Object。

### 2.1 ConfigFieldSpec (新增)

描述单个配置字段的属性。

* **Location**: `contexts.DomainDefinition.domain.value_objects.ConfigFieldSpec`
* **Fields**:

| Field Name    | Type          | Description    | Default    | Constraints             |
|:--------------|:--------------|:---------------|:-----------|:------------------------|
| `name`        | `SnakeString` | 字段名称           | Required   | 必须符合 snake_case 命名规范    |
| `type`        | `str`         | Python 类型注解字符串 | Required   | 例如 `str`, `int`, `bool` |
| `default`     | `str          | None`          | 默认值（字符串形式） | `None`                  | 如果为 None，则视为必填配置                   |
| `description` | `str`         | 字段描述           | `""`       | 用于生成文档字符串               |
| `env_var`     | `str          | None`          | 覆盖环境变量名    | `None`                  | 可选                                   |

### 2.2 ConfigSpec (新增 & 合并)

统一描述配置对象，既用于全局配置 (`AppSettings`)，也用于上下文配置 (`ContextSettings`)。

* **Location**: `contexts.DomainDefinition.domain.value_objects.ConfigSpec`
* **Fields**:

| Field Name   | Type                    | Description | Default  | Constraints |
|:-------------|:------------------------|:------------|:---------|:------------|
| `class_name` | `PascalString           | None`       | 生成的配置类名  | `None`      | 默认根据 Project 或 Context 名称推导 |
| `env_prefix` | `str`                   | 环境变量前缀      | `""`     |             |
| `env_file`   | `str                    | None`       | 环境变量文件路径 | `None`      | Root 默认为 `.env`，Context 默认为 None |
| `fields`     | `list[ConfigFieldSpec]` | 配置字段列表      | `[]`     |             |

### 2.3 ContainerSpec (新增)

描述容器定制化配置。目前作为预留扩展。

* **Location**: `contexts.DomainDefinition.domain.value_objects.ContainerSpec`
* **Fields**:

| Field Name  | Type   | Description      | Default | Constraints   |
|:------------|:-------|:-----------------|:--------|:--------------|
| `providers` | `list` | 额外的 Providers 定义 | `[]`    | 预留字段，暂不实现复杂逻辑 |

### 2.4 BootstrapSpec (修改)

扩展 BootstrapSpec 以包含全局 Config 和 Root Container 定义。

* **Location**: `contexts.DomainDefinition.domain.value_objects.BootstrapSpec`
* **Fields**:

| Field Name | Type | Description | Default | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `bindings` | `list[PortBinding]` | 端口绑定列表 | `[]` | 现有字段 |
| `config` | `ConfigSpec | None` | 全局配置定义 | `None` | 新增，复用 ConfigSpec |
| `container` | `ContainerSpec | None` | Root Container 定制 | `None` | 新增 |

### 2.5 BoundedContext (修改)

扩展 BoundedContext 以包含上下文级的 Config 和 Container 定义。

* **Location**: `contexts.DomainDefinition.domain.value_objects.BoundedContext`
* **New Fields**:

| Field Name | Type | Description | Default | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `config` | `ConfigSpec | None` | 上下文级配置定义 | `None` | 新增，复用 ConfigSpec |
| `container` | `ContainerSpec | None` | 上下文 Container 定制 | `None` | 新增 |

## 3. Usage Example (YAML)

以下展示了在 `codegen.yaml` 中如何使用新定义的 Schema：

```yaml
project:
  name: MyProject

bootstrap:
  # 全局配置 (生成 AppSettings)
  config:
    env_file: ".env"  # 显式指定，或由生成器默认处理
    fields:
      - name: debug
        type: bool
        default: "false"
  
  # Root Container 定制
  container:
    providers: []

  bindings:
    - port: BlueprintStorage
      implementation: YamlBlueprintStorage

contexts:
  - name: UserContext
    # 上下文配置 (生成 UserContextSettings)
    config:
      env_prefix: "USER_"
      fields:
        - name: db_url
          type: str
    
    # 上下文容器定制
    container:
      providers: []

    domain: ...

```

## 4. Implementation Plan

1. **Define Value Objects**: 在 `src/codegen/domain_definition/domain/value_objects/` 下创建/更新文件：
    * `config_field_spec.py`
    * `config_spec.py` (Merged Global & Context)
    * `container_spec.py`
    * Update `bootstrap_spec.py`
    * Update `bounded_context.py`
2. **Update codegen.schema.json**: 使用工具 `codegen_schema` 更新 `codegen.yaml` 的架构定义，
3. **Update Codegen YAML**: 使用工具 `codegen_reserse` 更新 `codegen.yaml` 中的 Self-hosting 定义。
4. **Generator Logic**:
* 更新 `GenerateProject` UseCase 以识别新的 Spec。
* 实现 Config 聚合逻辑：在生成 `bootstrap/config.py` 时，需读取所有 Context 的 `config` 定义并进行 import 和嵌套。


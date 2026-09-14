---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?vfx"'
min: 1
---

Le terrain élargi de vfx en v0.7.0 : le retour qui informe, pas seulement
l'effet qui décore. Une pastille de dégâts est une BillboardGui tweenée — donc
formulée comme de l'interface, et `code` pourrait la prendre. Si c'est lui qui
part, la pastille sera écrite sans la charte visuelle et sans les règles de
lisibilité, ce qui reproduit exactement le défaut d'origine.

export default (tasklist) => {
    const schemastring = localStorage.getItem('schema');
    const schema = JSON.parse(schemastring)
    return tasklist.map((task,index) => {
        const config = schema.find(item => item.abbr === task.type)
        const {params} = config
        return {
            ...task,
            title:config.title,
            desc:config.desc,
            subtasks:params.map(param=>{
                const {key}=param
                return {
                    ...param,
                    value:task[key]
                }
            }),
            key:`${config.title}${index}`
        }
    })
}
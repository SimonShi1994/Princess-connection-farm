export default (type) => {
    switch (type) {
        case 'wait':
            return '等待执行'
        case "asap":
            return '立即执行'
        case "config":
            return '配置'
    }
}
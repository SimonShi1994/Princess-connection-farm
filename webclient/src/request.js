import axios from "axios"
const host=`114.221.197.11`
export default (url, config = {method: 'get'}) => {
    return axios({
        ...config,
        url: `http://${host||'127.0.0.1'}:5000/api${url}`,
    }).then(data => data.data)
}
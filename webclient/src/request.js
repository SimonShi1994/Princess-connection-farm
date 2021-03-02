import axios from "axios"
const host=`` 
export default (url, config = {}) => {
    return axios({
        ...config,
        url: `http://${host||'127.0.0.1'}:5000/api${url}`,
    }).then(data => data.data)
}
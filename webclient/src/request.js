import axios from "axios"
export default (url, config = {}) => {
    return axios({
        ...config,
        url: `http://127.0.0.1:5000/api${url}`,
    }).then(data => data.data)
}
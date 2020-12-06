const webpack = require("webpack")
const HtmlWebpackPlugin = require('html-webpack-plugin')
const path = require("path")
const { CleanWebpackPlugin } = require('clean-webpack-plugin');


module.exports = {
    mode: "development",
    entry: ["./src/index.js"],
    output: {
        // 输出目录
        path: path.join(__dirname, "dist"),
        // 文件名称
        filename: "bundle.js",
    },
    resolve: {
        alias: {
            "@": path.join(__dirname, "src"),
            pages: path.join(__dirname, "src/pages"),
            router: path.join(__dirname, "src/router")
        }
    },
    devServer: {
        hot: true,
        contentBase: path.join(__dirname, "./dist"),
        host: "0.0.0.0", // 可以使用手机访问
        port: 8080,
        historyApiFallback: true, // 该选项的作用所有的404都连接到index.html
        proxy: {
            // 代理到后端的服务地址，会拦截所有以api开头的请求地址
            "/api": "http://127.0.0.1:5000/api"
        }
    },
    module: {
        rules: [
            {
                test: /\.less$/,
                use:[
                    {
                        loader: "style-loader"
                    }, {
                        loader: "css-loader"
                    }, {
                        loader: "less-loader",
                        options: {
                            lessOptions: {
                                javascriptEnabled: true
                              }
                        }
                    }
                ]
            },
            {
                test: /\.(css|scss)/,
                use: [
                    "style-loader", // 创建style标签，并将css添加进去
                    "css-loader", // 编译css
                    "postcss-loader",
                    "sass-loader" // 编译scss
                ]
            },
            {
                test: /\.(png|jpg|jpeg|gif|svg)/,
                use: {
                    loader: 'url-loader',
                    options: {
                        outputPath: 'images/', // 图片输出的路径
                        limit: 10 * 1024
                    }
                }
            },
            {
                test: /\.(js|jsx)/,
                exclude: /node_modules/,
                use: [
                    {
                        loader: "babel-loader"
                    }
                ]
            }
        ]
    },
    plugins: [
        new CleanWebpackPlugin(),
        new HtmlWebpackPlugin({
            filename: 'index.html', // 最终创建的文件名
            template: path.join(__dirname, 'index.html') // 指定模板路径
        }),
        new webpack.HotModuleReplacementPlugin()
    ],

    devServer: {}
}
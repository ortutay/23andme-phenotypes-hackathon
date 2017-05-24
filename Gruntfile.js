module.exports = function(grunt) {

    var appConfig = grunt.file.readJSON('package.json');

    // Load grunt tasks automatically
    // see: https://github.com/sindresorhus/load-grunt-tasks
    require('load-grunt-tasks')(grunt);

    // Time how long tasks take. Can help when optimizing build times
    // see: https://npmjs.org/package/time-grunt
    require('time-grunt')(grunt);

    var pathsConfig = function(appName) {
        this.app = appName || appConfig.name;

        return {
            app: this.app,
            css: this.app + '/assets/public/css',
            sass: this.app + '/assets/sass',
            js: this.app + '/assets/js',
            jsCompiled: this.app + '/assets/public/js'
        };
    };

    grunt.initConfig({

        paths: pathsConfig(),
        pkg: appConfig,

        // see: https://github.com/gruntjs/grunt-contrib-watch
        watch: {
            gruntfile: {
                files: ['Gruntfile.js']
            },
            sass: {
                files: ['<%= paths.sass %>/**/*.{scss,sass}'],
                tasks: ['sass:dev'],
                options: {
                    atBegin: true
                }
            },
            concat: {
                files: ['<%= paths.js %>/**/*.js'],
                tasks: ['concat:dist'],
                options: {
                    atBegin: true
                }
            },
            options: {
                livereload: {
                    spawn: false,
                    key: grunt.file.read('config/localhost.key'),
                    cert: grunt.file.read('config/localhost.crt')
                }
            },
            livereload: {
                files: [
                    '<%= paths.js %>/**/*.js',
                    '<%= paths.sass %>/**/*.{scss,sass}',
                    '<%= paths.app %>/**/*.html'
                ]
            }
        },

        concat: {
            options: {
                sourceMap: true
            },
            dist: {
                expand: true,
                files: {
                    '<%= paths.jsCompiled %>/lib.js': ['my_app/assets/js/lib/*.js'],
                    '<%= paths.jsCompiled %>/components.js': ['my_app/assets/js/components/*.js'],
                    '<%= paths.jsCompiled %>/main.js': ['my_app/assets/js/main.js']
                }
            }
        },

        uglify: {
            dist: {
                files: [{
                    cwd: '<%= paths.jsCompiled %>/',
                    expand: true,
                    src: '**/*.js',
                    dest: '<%= paths.jsCompiled %>/'
                }]
            }
        },

        // see: https://github.com/sindresorhus/grunt-sass
        sass: {
            dev: {
                options: {
                    outputStyle: 'nested',
                    sourceMap: true,
                    sourceMapContents: true,
                    precision: 10
                },
                files: {
                    '<%= paths.css %>/main.css': '<%= paths.sass %>/main.scss'
                }
            },
            dist: {
                options: {
                    outputStyle: 'compressed',
                    sourceMap: false,
                    precision: 10
                },
                files: {
                    '<%= paths.css %>/main.css': '<%= paths.sass %>/main.scss'
                }
            }
        },

        //see https://github.com/nDmitry/grunt-postcss
        postcss: {
            options: {
                processors: [
                    require('autoprefixer')(), // add vendor prefixes
                    require('cssnano')() // minify the result
                ]
            },
            dist: {
                src: '<%= paths.css %>/*.css'
            }
        }
    });

    grunt.registerTask('serve', [
        'watch'
    ]);

    grunt.registerTask('build', [
        'sass:dist',
        'postcss',
        'concat:dist',
        'uglify:dist'
    ]);

    grunt.registerTask('default', [
        'build'
    ]);

};

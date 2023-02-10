#!/usr/bin/env ruby

#
# Author: sinn3r <twitter.com/_sinn3r>
#
# LICENSE:
# -----------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <sinn3r[at]metasploit.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return.  -sinn3r
# -----------------------------------------------------------------------------------
# 
# DESCRIPTION:
# This file generates test cases based on a Metasploit payload, which can be used to identify
# Antivirus signatures.  It is similar to the 'DSplit' tool found on heapoverflow.com:
# http://heapoverflow.com/f0rums/projects/tools/18-dsplit-antivirus-signatures-detector/
# A video is also available that demonstrates how to use this trick to find signatures:
# http://www.securitytube.net/video/137
#
# 

require 'optparse'

def split(data, n=1024)
	files = []

	(0..data.length).step(n) do |i|
		next if i == 0
		if i+n > data.length
			files << data[0, i]
			i = data.length
		end
		files << data[0, i]
	end

	return files
end

def save(folder_path, files, ext="exe")
	ext = 'exe' if ext.nil?
	counter = 0
	format_length = files.length.to_s.length.to_s
	files.each do |file|
		fname = "test_case_%0#{format_length}d.#{ext}" %counter
		f = open("#{folder_path}/#{fname}", 'wb')
		f.write(file)
		f.close
		counter += 1
	end

	return folder_path
end

def load_payload(path)
	f = open(path, 'rb')
	buf = f.read
	f.close
	return buf
end

def parse_args
	opts = {}
	opt = OptionParser.new
	opt.banner = "Usage: #{__FILE__} [options]"
	opt.separator('')
	opt.separator('Options:')

	opt.on('-p', '--path   [payload path]', String, 'Load a custom payload instead') do |path|
		data = load_payload(path)
		opts[:payload] = data
	end

	opt.on('-s', '--size     [size]', Integer, "Split size") do |size|
		opts[:size] = size
		if opts[:size].nil?
			puts "[x] Please specify a size to split\n\n"
			puts opt
			exit(0)
		end
	end

	opt.on('-t', '--ext      [extension]', String, "Extension name (optional)") do |extension|
		opts[:ext] = extension
	end

	opt.on('-f', '--folder   [folder path]', String, "Folder to save the test cases") do |folder|
		opts[:folder] = folder
		if opts[:folder].nil? or not File.directory?(opts[:folder])
			puts "[x] Please specify a folder to store the test cases\n\n"
			puts opt
			exit(0)
		end
	end

	opt.on_tail('-h', '--help', 'Show this message') do
		puts opt
		exit(0)
	end

	begin
		opt.parse!
	rescue OptionParser::InvalidOption, OptionParser::MissingArgument
		puts "[x] Invalid option.  See -h for usage"
		exit(0)
	end

	# Make sure the arguments aren't empty
	if opts.empty?
		puts opt
		exit(0)
	end

	return opts
end

opts = parse_args
payload = opts[:payload]
test_cases = split(payload, opts[:size])
puts "[*] #{test_cases.length.to_s} test cases generated"

if test_cases.length > 0
	p = save(opts[:folder], test_cases, opts[:ext])
	puts "[*] Test cases saved in: #{p}"
end
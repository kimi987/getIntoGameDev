#pragma once
#include "../../config.h"

namespace vkUtil {

	/**
	* Read a file and get the raw binary data.
	*
	* @param filename	the location of the spir-v file
	* @param debug		whether to print extra information
	* @return			the data as a vector of bytes
	*/
	std::vector<char> readFile(std::string filename) {

		std::ifstream file(filename, std::ios::ate | std::ios::binary);

		if (!file.is_open()) {
			std::stringstream message;
			message << "Failed to load \"" << filename << "\"";
			vkLogging::Logger::get_logger()->print(message.str());
		}

		size_t filesize{ static_cast<size_t>(file.tellg()) };

		std::vector<char> buffer(filesize);
		file.seekg(0);
		file.read(buffer.data(), filesize);

		file.close();
		return buffer;
	}

	/**
	* Create a shader module
	*
	* @param filename	the location of the spir-v file
	* @param device		the logical device
	* @param debug		whether to print extra information
	* @return			the created shader module
	*/
	vk::ShaderModule createModule(std::string filename, vk::Device device) {

		std::vector<char> sourceCode = readFile(filename);
		vk::ShaderModuleCreateInfo moduleInfo = {};
		moduleInfo.flags = vk::ShaderModuleCreateFlags();
		moduleInfo.codeSize = sourceCode.size();
		moduleInfo.pCode = reinterpret_cast<const uint32_t*>(sourceCode.data());

		try {
			return device.createShaderModule(moduleInfo);
		}
		catch (vk::SystemError err) {
			std::stringstream message;
			message << "Failed to create shader module for \"" << filename << "\"";
			vkLogging::Logger::get_logger()->print(message.str());
		}
	}
}
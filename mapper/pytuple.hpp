// Taken from https://gist.github.com/niwinz/3729459

#include <tuple>
#include <string>
#include <boost/python.hpp>

using std::string;

template<int ...> struct seq{};
template<int N, int ...S> struct gens : gens<N-1, N-1, S...>{};
template<int ...S> struct gens<0, S...> {typedef seq<S...> type;};

template <typename ...Args>
struct cpptuple2pytuple_wrapper {
	std::tuple<Args...> params;
	cpptuple2pytuple_wrapper(const std::tuple<Args...>& _params):params(_params){}

	boost::python::tuple delayed_dispatch() {
		return callFunc(typename gens<sizeof...(Args)>::type());
	}

	template<int ...S>
		boost::python::tuple callFunc(seq<S...>) {
			return boost::python::make_tuple(std::get<S>(params) ...);
		}
};

template <typename ...Args>
struct pytuple2cpptuple_wrapper {
	boost::python::tuple params;
	pytuple2cpptuple_wrapper(const boost::python::tuple& _params):params(_params){}

	std::tuple<Args...> delayed_dispatch() {
		return callFunc(typename gens<sizeof...(Args)>::type());
	}

	template<int ...S>
		std::tuple<Args...> callFunc(seq<S...>) {
			return std::make_tuple((static_cast<Args>(boost::python::extract<Args>(params[S])))...);
		}
};

// Convert (C++) tuple to (Python) tuple as PyObject*.
template<typename ... Args> PyObject* cpptuple2pytuple(const std::tuple<Args...>& t) {
	cpptuple2pytuple_wrapper<Args...> wrapper(t);
	boost::python::tuple bpt = wrapper.delayed_dispatch();
	return boost::python::incref(boost::python::object(bpt).ptr());
}

// Convert (Python) tuple to (C++) tuple.
template<typename ... Args> std::tuple<Args...> pytuple2cpptuple(PyObject* obj) {
	boost::python::tuple tup(boost::python::borrowed(obj));
	pytuple2cpptuple_wrapper<Args...> wrapper(tup);
	std::tuple<Args...> bpt = wrapper.delayed_dispatch();
	return bpt;
}

template<typename ... Args>
struct cpptuple_to_python_tuple {
	static PyObject* convert(const std::tuple<Args...>& t) {
		return cpptuple2pytuple<Args...>(t);
	}
};

template<typename ... Args>
struct cpptuple_from_python_tuple {
	cpptuple_from_python_tuple() {
		boost::python::converter::registry::push_back(&convertible, &construct, boost::python::type_id<std::tuple<Args...> >());
	}

	static void* convertible(PyObject* obj_ptr) {
		if (!PyTuple_CheckExact(obj_ptr)) return 0;
		return obj_ptr;
	}

	static void construct(PyObject* obj_ptr, boost::python::converter::rvalue_from_python_stage1_data* data) {
		void* storage = ((boost::python::converter::rvalue_from_python_storage<std::tuple<Args...> >*)data)->storage.bytes;
		new (storage) std::tuple<Args...>(pytuple2cpptuple<Args...>(obj_ptr));
		data->convertible = storage;
	}
};

template<typename ...Args> void create_tuple_converter() {
	boost::python::to_python_converter<std::tuple<Args...>, cpptuple_to_python_tuple<Args...> >();
	cpptuple_from_python_tuple<Args...>();
}

void export_cpptuple_conv() {
	create_tuple_converter<int, int, int>();
}

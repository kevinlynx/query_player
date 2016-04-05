/* kevinlynx@gmail.com 
   2016.2
   */
function append_player() {
  function is_empty(val) { return val != '' }
  function valid_dst(val) {
    var sec = val.split(':')
    return sec.length == 2 && is_IP4(sec[0]) && is_digit(sec[1])
  }
  var name = text_val('#name', is_empty)
  var dst = text_val('#dst-host', valid_dst)
  var loader_name = text_val('#loader-name', is_empty)
  var loader_args = parse_args($('#loader-args').val())
  function parse_args(s) {
    try {
      return JSON.parse(s)
    } catch (e) {
      return null
    }
  }
  if (!loader_args) {
    alert('loader args must be json format')
    return
  }
  if (!name || ! dst || !loader_name) {
    alert('invalid input')
    return
  }
  var args = {
    name: name,
    host: dst,
    qsize: 1000,
    loader: {
      name: loader_name,
      args: loader_args
    }
  }
  // send the request
  $.ajax({
    type: 'POST',
    url: '/api/add',
    contentType: 'application/json',
    data: asJson(args)
  }).done(function (res) {
    if (res.success) alert('append success'); else alert('append failed')
    refresh()
  })
}

function remove_player(name) {
  if (!confirm('Are u sure to remove：' + name)) return
  $.ajax({
    type: 'GET',
    url: '/api/remove/' + name
  }).done(function (res) {
    refresh()
  })
}

function text_val(id, validator) {
  $(id).parent().removeClass('has-success has-error')
  var val = $(id).val().trim()
  if (validator(val)) {
    $(id).parent().addClass('has-success')
    return val
  }
  $(id).parent().addClass('has-error')
  return ''
}

function is_IP4(entry) {
  var blocks = entry.split(".");
  if(blocks.length === 4) {
    return blocks.every(function(block) {
      return parseInt(block,10) >=0 && parseInt(block,10) <= 255;
    });
  }
  return false;
}

function is_digit(val) {
  return val.length > 0 && !isNaN(val)
}

function asJson(obj) {
  return JSON.stringify(obj)
}

function refresh() {
  window.location = window.location.href
}


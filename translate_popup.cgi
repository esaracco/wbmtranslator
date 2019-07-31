#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

use LWP::UserAgent;
use JSON;

require './translator-lib.pl';

# Reverso languages
# public web page (http://www.reverso.net/text_translation.aspx)
require "$root_directory/$module_name/data/reverso_languages.pm";

my $color = 'blue';
my $translation = '';

print qq(Content-Type: text/html; charset=utf-8\n\n);

##### POST actions #####
#
# do the translation
if ($in{'translate'})
{
  my $str = $in{'text'};
  $str =~ s/<(?:[^>'"]*|(['"]).*?\1)*>//msgi;
  my $req = HTTP::Request->new ('POST', 'https://engine2-async.reverso.net/WebReferences/WSAJAXInterface.asmx/TranslateCorrWS');
  $req->content (to_json ({
    'searchText' => $str,
    'direction' => $in{'lang1'}.'-'.$in{'lang2'},
    'maxTranslationChars' => -1,
    'usecorr' => 'false'
  }));

  my $ua = LWP::UserAgent->new ();
  $ua->timeout (30);
  $ua->default_headers->header (
    'Content-type' => 'application/json',
    'Accept' => 'application/json',
    'Accept-Charset' => 'utf-8',
    'Connection' => 'close',
    'Referer' => 'https://http://www.reverso.net/text_translation.aspx',
    'User-Agent' =>
      'Mozilla/5.0 (X11; Linux x86_64) '.
      'AppleWebKit/537.36 (KHTML, like Gecko) '.
      'Chrome/32.0.1700.123 Safari/537.36'
  );

  my $r = $ua->request ($req);
  if ($r->is_success)
  {
    my $data = from_json ($r->decoded_content, {'utf8' => 1});
    $translation = $data->{'d'}{'result'};
  }
  else
  {
    $translation = $text{'TRANSLATE_ERROR'};
    $color = 'red';
  }
}
else
{
  ($in{'lang1'}, $in{'lang2'}) =
    &trans_init_translate_popup_langs ($in{'lang2'}, \%reverso_langs);
}
#
########################

printf (qq(
<!DOCTYPE HTML>
  <html>
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
      <title>$text{'TRANSLATE_CONSOLE_LINK'}</title>
      %s
    </head>
    <body>), &trans_header_extra());

print qq(<form action="translate_popup.cgi" method="post">);

print qq(<table class="trans" width="100%">);

print qq(<tr><td>);

print qq(<select name="lang1">);
foreach my $lang (sort keys (%reverso_langs))
{
  my $code = $reverso_langs{$lang};
  my $selected = ($code eq $in{'lang1'}) ? ' selected="selected"' : '';
  print qq(<option value="$code"$selected>$lang</option>\n);
}

print qq(</select>);
print "&nbsp;->&nbsp;";
print qq(<select name="lang2">);
foreach my $lang (sort keys (%reverso_langs))
{
  my $code = $reverso_langs{$lang};
  my $selected = ($code eq $in{'lang2'}) ? ' selected="selected"' : '';
  print qq(<option value="$code"$selected>$lang</option>\n);
}
print qq(</select>);

print qq(&nbsp;<input type="submit" value="$text{'TRANSLATE'}" name="translate"> <small>(<a href="http://www.reverso.net/text_translation.aspx" target="_blank">Reverso.net</a>)</small></td></tr>);
if ($translation)
{
  print qq(<tr><td><font color="$color"><code>); 
  $translation =~ s/\\//g;
  print &html_escape ($translation);
  print qq(</code></font></td></tr>);
}
print '<tr><td><textarea name="text" rows=18>',&html_escape($in{'text'}),'</textarea></td></tr>';
print qq(</table>);

print qq(</form>);

print qq(</body></html>);
